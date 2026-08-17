"""
Simplified pressure intensity calculation using Carry events.

Uses only Carry events and their defensive_responsibility.probability_sum,
weighted by carry duration to provide a fast, direct pressure metric.

Key approach:
- Extract only Carry events from sequence
- Get probability_sum from defensive_responsibility
- Weight each carry by its duration
- Aggregate weighted sums
- Normalize by total duration
"""

import pandas as pd
from typing import List, Dict, Tuple


def calculate_sequence_pressure(
    events_sequence: List[Dict] | pd.DataFrame,
    team: str = None
) -> Dict:
    """
    Calculate pressure intensity for a sequence using only Carry events.

    Uses probability_sum from defensive_responsibility, weighted by carry duration.

    Args:
        events_sequence: List of event dicts or DataFrame
        team: Team to analyze (optional, uses all carry events if None)

    Returns:
        Dict with pressure metrics:
        {
            'mean_pressure': float (0-1),
            'max_pressure': float (0-1),
            'total_weighted_pressure': float,
            'total_carry_duration': float,
            'carry_count': int,
            'carries_analyzed': int,
            'intensity_level': str ('LOW', 'MEDIUM', 'HIGH', 'EXTREME'),
        }
    """
    # Convert DataFrame to list of dicts if needed
    if isinstance(events_sequence, pd.DataFrame):
        events_sequence = events_sequence.to_dict('records')

    if not events_sequence:
        return _empty_pressure_result()

    # Extract Carry events
    carry_events = _extract_carry_events(events_sequence, team)

    if not carry_events:
        return _empty_pressure_result()

    # Calculate weighted pressure
    weighted_pressures = []
    total_weighted_pressure = 0.0
    total_duration = 0.0
    max_pressure = 0.0
    
    for carry_event in carry_events:
        # Get probability_sum from defensive_responsibility
        pressure_value = _get_probability_sum(carry_event)

        # Get carry duration
        duration = _get_carry_duration(carry_event)

        if duration > 0:
            # Weight pressure by duration
            weighted_pressure = pressure_value * duration

            weighted_pressures.append(pressure_value)
            total_weighted_pressure += weighted_pressure
            total_duration += duration
            max_pressure = max(max_pressure, pressure_value)

    # Calculate mean pressure (weighted by duration)
    if total_duration > 0:
        mean_pressure = total_weighted_pressure / total_duration
    else:
        mean_pressure = 0.0

    # Determine intensity level
    intensity_level = _determine_intensity_level(mean_pressure)

    return {
        'mean_pressure': round(mean_pressure, 3),
        'max_pressure': round(max_pressure, 3),
        'total_weighted_pressure': round(total_weighted_pressure, 3),
        'total_carry_duration': round(total_duration, 3),
        'carry_count': len(carry_events),
        'carries_analyzed': len(weighted_pressures),
        'intensity_level': intensity_level,
        'pressure_values': [round(p, 3) for p in weighted_pressures],
    }


def _extract_carry_events(events_sequence: List[Dict], team: str = None) -> List[Dict]:
    """
    Extract Carry events from sequence.

    Args:
        events_sequence: List of events
        team: Optional team filter

    Returns:
        List of Carry events
    """
    carry_events = []

    for event in events_sequence:
        event_type = event.get('type_name') or event.get('type', {}).get('name')

        if event_type == 'Carry':
            # Filter by team if specified
            if team:
                event_team = event.get('team')
                if isinstance(event_team, dict):
                    event_team = event_team.get('name')

                if event_team != team:
                    continue

            carry_events.append(event)

    return carry_events


def _get_probability_sum(carry_event: Dict) -> float:
    """
    Extract probability_sum from defensive_responsibility.

    Args:
        carry_event: Carry event dict

    Returns:
        float: probability_sum value (0-1), or 0 if not available
    """
    def_resp = carry_event.get('defensive_responsibility')

    if not def_resp or not isinstance(def_resp, dict):
        return 0.0

    prob_sum = def_resp.get('probability_sum', 0.0)

    if isinstance(prob_sum, (int, float)):
        return min(float(prob_sum), 1.0)

    return 0.0


def _get_carry_duration(carry_event: Dict) -> float:
    """
    Extract carry duration in seconds.

    Args:
        carry_event: Carry event dict

    Returns:
        float: duration in seconds, or 0 if not available
    """
    # StatsBomb events have duration field at top level
    duration = carry_event.get('duration', 0.0)

    if isinstance(duration, (int, float)):
        return float(duration)

    return 0.0


def _determine_intensity_level(pressure_score: float) -> str:
    """
    Convert pressure score to intensity level.

    Args:
        pressure_score: Score 0-1

    Returns:
        str: 'LOW', 'MEDIUM', 'HIGH', or 'EXTREME'
    """
    if pressure_score < 0.15:
        return 'LOW'
    elif pressure_score < 0.35:
        return 'MEDIUM'
    else:
        return 'EXTREME'


def _empty_pressure_result() -> Dict:
    """Return empty result when no data available."""
    return {
        'mean_pressure': 0.0,
        'max_pressure': 0.0,
        'total_weighted_pressure': 0.0,
        'total_carry_duration': 0.0,
        'carry_count': 0,
        'carries_analyzed': 0,
        'intensity_level': 'LOW',
        'pressure_values': [],
    }


# Export main function
__all__ = ['calculate_sequence_pressure']
