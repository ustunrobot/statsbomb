"""
Pressure intensity quantification utilities.

Combines pressure_like_probability, under_pressure flag, and defensive events
to create comprehensive pressure intensity scores.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


def calculate_sequence_pressure_intensity(
    events_sequence: List[Dict],
    opponent_team: str = None,
    weighted: bool = True
) -> Dict:
    """
    Calculate pressure intensity for a sequence of events.

    Combines three pressure signals:
    1. pressure_like_probability (predictive risk)
    2. under_pressure flag (realized constraint)
    3. Nearby defensive events (context)

    Args:
        events_sequence: List of event dicts from match
        opponent_team: Team name applying pressure (auto-detect if None)
        weighted: If True, use event-type-specific weights (recommended)

    Returns:
        Dict with pressure metrics:
        {
            'mean_pressure': float (0-1),
            'max_pressure': float (0-1),
            'min_pressure': float (0-1),
            'std_pressure': float,
            'event_scores': List[float],
            'intensity_level': str ('LOW', 'MEDIUM', 'HIGH', 'EXTREME'),
            'distribution': Dict with pressure quartile breakdown,
            'high_pressure_events': List of high-risk events,
            'pressure_peak': Dict with peak pressure moment,
        }
    """
    if not events_sequence:
        return {
            'mean_pressure': 0.0,
            'max_pressure': 0.0,
            'min_pressure': 0.0,
            'std_pressure': 0.0,
            'event_scores': [],
            'intensity_level': 'LOW',
            'distribution': {'low': 0, 'moderate': 0, 'high': 0, 'extreme': 0},
            'high_pressure_events': [],
            'pressure_peak': None,
        }

    # Auto-detect opponent team if not provided
    if opponent_team is None:
        teams = set()
        for event in events_sequence:
            team = event.get('team', {}).get('name') if isinstance(event.get('team'), dict) else event.get('team')
            if team:
                teams.add(team)
        if len(teams) > 1:
            # Take first non-majority team as opponent
            opponent_team = min(teams, key=lambda t: sum(1 for e in events_sequence if e.get('team') == t))

    # Calculate pressure score for each event
    event_scores = []
    for i, event in enumerate(events_sequence):
        score = _calculate_event_pressure_score(
            event=event,
            events_sequence=events_sequence,
            event_index=i,
            opponent_team=opponent_team,
            weighted=weighted
        )
        event_scores.append(score)

    # Aggregate metrics
    if event_scores:
        mean_pressure = np.mean(event_scores)
        max_pressure = np.max(event_scores)
        min_pressure = np.min(event_scores)
        std_pressure = np.std(event_scores) if len(event_scores) > 1 else 0.0
    else:
        mean_pressure = max_pressure = min_pressure = std_pressure = 0.0

    # Determine intensity level
    intensity_level = _determine_intensity_level(mean_pressure)

    # Distribution (quartiles)
    distribution = _calculate_pressure_distribution(event_scores)

    # Find high-pressure events (>0.5)
    high_pressure_events = [
        (i, events_sequence[i], score)
        for i, score in enumerate(event_scores)
        if score > 0.5
    ]

    # Find pressure peak
    pressure_peak = None
    if high_pressure_events:
        peak_idx = np.argmax(event_scores)
        peak_event = events_sequence[peak_idx]
        peak_score = event_scores[peak_idx]
        pressure_peak = {
            'event_index': peak_idx,
            'event_type': peak_event.get('type', {}).get('name') if isinstance(peak_event.get('type'), dict) else peak_event.get('type'),
            'player': peak_event.get('player', {}).get('name') if isinstance(peak_event.get('player'), dict) else peak_event.get('player'),
            'pressure_score': peak_score,
            'intensity_level': _determine_intensity_level(peak_score),
        }

    return {
        'mean_pressure': round(mean_pressure, 3),
        'max_pressure': round(max_pressure, 3),
        'min_pressure': round(min_pressure, 3),
        'std_pressure': round(std_pressure, 3),
        'event_scores': [round(s, 3) for s in event_scores],
        'intensity_level': intensity_level,
        'distribution': distribution,
        'high_pressure_events': len(high_pressure_events),
        'high_pressure_event_indices': [idx for idx, _, _ in high_pressure_events],
        'pressure_peak': pressure_peak,
        'sequence_length': len(events_sequence),
    }


def _calculate_event_pressure_score(
    event: Dict,
    events_sequence: List[Dict],
    event_index: int,
    opponent_team: str = None,
    weighted: bool = True
) -> float:
    """
    Calculate pressure score for a single event (0-1 scale).

    Combines three signals with event-type-specific weights:
    1. pressure_like_probability (from defensive_responsibility)
    2. under_pressure flag
    3. Nearby opponent pressure/defensive events

    Args:
        event: Single event dict
        events_sequence: Full sequence for context
        event_index: Position in sequence
        opponent_team: Opponent team name
        weighted: Use event-type-specific weights

    Returns:
        float: Pressure score 0-1
    """
    # Extract signals
    pressure_prob = _get_pressure_like_probability(event)
    under_pressure = event.get('under_pressure', False) or False
    nearby_event = _check_nearby_defensive_event(events_sequence, event_index, opponent_team)

    event_type = event.get('type', {}).get('name') if isinstance(event.get('type'), dict) else event.get('type')

    # Select weights based on event type
    if weighted:
        if event_type == 'Carry':
            weights = {'prob': 0.50, 'flag': 0.30, 'event': 0.20}
        elif event_type == 'Pass':
            weights = {'prob': 0.30, 'flag': 0.50, 'event': 0.20}
        elif event_type == 'Shot':
            weights = {'prob': 0.30, 'flag': 0.40, 'event': 0.30}
        else:
            weights = {'prob': 0.33, 'flag': 0.33, 'event': 0.34}
    else:
        # Equal weights if not using event-specific
        weights = {'prob': 0.33, 'flag': 0.33, 'event': 0.34}

    # Calculate hybrid score
    score = (
        (pressure_prob * weights['prob']) +
        (int(bool(under_pressure)) * weights['flag']) +
        (int(nearby_event) * weights['event'])
    )

    return min(score, 1.0)  # Cap at 1.0


def _get_pressure_like_probability(event: Dict) -> float:
    """
    Extract maximum pressure_like_probability from defensive_responsibility.

    Args:
        event: Event dict containing defensive_responsibility field

    Returns:
        float: Max probability (0-1) or 0 if not available
    """
    if 'defensive_responsibility' not in event:
        return 0.0

    def_resp = event['defensive_responsibility']

    # Handle None or missing defensive_responsibility
    if not def_resp or not isinstance(def_resp, dict):
        return 0.0

    max_prob = 0.0

    for player in def_resp.get('players', []):
        prob = player.get('pressure_like_probability', 0.0)
        if prob and isinstance(prob, (int, float)):
            max_prob = max(max_prob, float(prob))

    return min(max_prob, 1.0)


def _check_nearby_defensive_event(
    events_sequence: List[Dict],
    current_index: int,
    opponent_team: str = None
) -> bool:
    """
    Check if defensive event occurs near current event (within 1-2 indices).

    Args:
        events_sequence: Full event sequence
        current_index: Current event position
        opponent_team: Opponent team name

    Returns:
        bool: True if pressure/duel/interception nearby
    """
    if current_index >= len(events_sequence) - 1:
        return False

    # Check next 1-2 events
    for i in range(current_index + 1, min(current_index + 3, len(events_sequence))):
        next_event = events_sequence[i]
        event_type = next_event.get('type', {}).get('name') if isinstance(next_event.get('type'), dict) else next_event.get('type')
        team = next_event.get('team', {}).get('name') if isinstance(next_event.get('team'), dict) else next_event.get('team')

        # Check for opponent defensive event
        if opponent_team and team == opponent_team:
            if event_type in ['Pressure', 'Duel', 'Interception', 'Clearance', 'Block']:
                return True

    return False


def _determine_intensity_level(pressure_score: float) -> str:
    """
    Convert pressure score to intensity level.

    Args:
        pressure_score: Score 0-1

    Returns:
        str: 'LOW', 'MEDIUM', 'HIGH', or 'EXTREME'
    """
    if pressure_score < 0.25:
        return 'LOW'
    elif pressure_score < 0.45:
        return 'MEDIUM'
    elif pressure_score < 0.65:
        return 'HIGH'
    else:
        return 'EXTREME'


def _calculate_pressure_distribution(scores: List[float]) -> Dict[str, int]:
    """
    Calculate quartile distribution of pressure scores.

    Args:
        scores: List of pressure scores (0-1)

    Returns:
        Dict with count in each quartile
    """
    if not scores:
        return {'low': 0, 'moderate': 0, 'high': 0, 'extreme': 0}

    low = sum(1 for s in scores if s < 0.25)
    moderate = sum(1 for s in scores if 0.25 <= s < 0.45)
    high = sum(1 for s in scores if 0.45 <= s < 0.65)
    extreme = sum(1 for s in scores if s >= 0.65)

    total = len(scores)

    return {
        'low': f"{low} ({100*low/total:.1f}%)" if total > 0 else "0 (0%)",
        'moderate': f"{moderate} ({100*moderate/total:.1f}%)" if total > 0 else "0 (0%)",
        'high': f"{high} ({100*high/total:.1f}%)" if total > 0 else "0 (0%)",
        'extreme': f"{extreme} ({100*extreme/total:.1f}%)" if total > 0 else "0 (0%)",
    }


def calculate_possession_pressure_intensity(
    events_df: pd.DataFrame,
    team: str,
    opponent_team: str = None,
) -> Dict:
    """
    Calculate pressure intensity for all possessions of a team in a match.

    Args:
        events_df: DataFrame with match events (from load_match_events)
        team: Team name to analyze
        opponent_team: Opponent team (auto-detect if None)

    Returns:
        Dict with pressure metrics for each possession
    """
    if opponent_team is None:
        teams = events_df['team'].dropna().unique()
        opponent_team = [t for t in teams if t != team][0] if len(teams) > 1 else None

    # Group by possession
    possessions = []
    current_possession = []

    for _, event in events_df.iterrows():
        current_possession.append(event.to_dict())

        # Check if possession changed
        if len(possessions) > 0 and event['team'] != events_df.iloc[-1]['team']:
            # Save current possession
            if current_possession and current_possession[0]['team'] == team:
                pressure_metrics = calculate_sequence_pressure_intensity(
                    current_possession,
                    opponent_team=opponent_team
                )
                possessions.append({
                    'sequence': current_possession,
                    'pressure': pressure_metrics,
                })
            current_possession = []

    return possessions
