"""
Buildup sequence builder.

Extracts buildup sequences from possession sequences.
Buildup = controlled possession from defensive third to opponent half with minimum 2 passes.
Excludes direct long passes (single-pass sequences).

Conditions:
  START: Ball event (Recovery, Clearance, GK) at x < 33.33 (first third)
  END:   x > 50 (crossed halfway) OR Shot OR Loss of possession
  EXTRACT: Only sequences with minimum 2 passes (filters out direct long balls)
  SUCCESS: Reached opponent half (x > 50) AND maintained possession
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict


def extract_buildups_from_sequences(
    sequences: List[pd.DataFrame],
    team: str,
    opponent_team: str = None,
    include_pressure: bool = True
) -> List[Dict]:
    """
    Extract buildup sequences from possession sequences.

    Args:
        sequences: List of possession sequence DataFrames (from sequence_builder)
        team: Team name to analyze
        opponent_team: Opponent team name (auto-detect if None)
        include_pressure: If True, calculate pressure metrics (requires pressure.py)

    Returns:
        List of buildup dicts with metrics
    """
    buildups = []
    buildup_id = 0

    for seq_idx, possession_seq in enumerate(sequences):
        # Extract buildups from this possession
        seq_buildups = _extract_buildups_from_possession(
            possession_seq=possession_seq,
            sequence_id=seq_idx,
            team=team,
            opponent_team=opponent_team,
            include_pressure=include_pressure
        )

        for buildup in seq_buildups:
            buildup['buildup_id'] = buildup_id
            buildups.append(buildup)
            buildup_id += 1

    return buildups


def _extract_buildups_from_possession(
    possession_seq: pd.DataFrame,
    sequence_id: int,
    team: str,
    opponent_team: str = None,
    include_pressure: bool = True
) -> List[Dict]:
    """
    Extract all buildups within a single possession sequence.

    Buildup must have minimum 2 passes (excludes direct long passes).

    Note: Uses sequence's end_reason to determine buildup outcome,
    since possession-changing events are not included in the sequence.

    Args:
        possession_seq: Single possession DataFrame from sequence_builder
        sequence_id: ID of parent sequence
        team: Team name
        opponent_team: Opponent team
        include_pressure: Calculate pressure metrics

    Returns:
        List of buildup dicts
    """
    buildups = []
    buildup_active = False
    buildup_start_idx = None
    buildup_events = []

    # Get the sequence's end reason (how this possession ended)
    sequence_end_reason = possession_seq['end_reason'].iloc[0] if len(possession_seq) > 0 else None

    for idx, (row_idx, event) in enumerate(possession_seq.iterrows()):
        event_type = event['type_name']
        event_x = event['x']
        event_team = event['team']

        # CHECK START CONDITION
        if not buildup_active and _check_buildup_start(event, team):
            buildup_active = True
            buildup_start_idx = idx
            buildup_events = [event]
            continue

        # COLLECT EVENTS DURING BUILDUP (only team's events)
        if buildup_active:
            # Only collect team's own events, not opponent events
            # (but still check all events for end conditions)
            if event_team == team:
                buildup_events.append(event)

            # CHECK END CONDITIONS (against all events to detect possession loss)
            should_end, end_reason = _check_buildup_end(
                events=buildup_events,
                current_event=event,
                team=team
            )

            if should_end:
                # Only extract if buildup has minimum 2 passes (excludes direct long passes)
                n_passes = sum(1 for e in buildup_events if e['type_name'] == 'Pass')

                if n_passes >= 2:
                    # Extract buildup metrics
                    buildup_data = _compute_buildup_metrics(
                        events=buildup_events,
                        sequence_id=sequence_id,
                        start_idx=buildup_start_idx,
                        end_idx=idx,
                        end_reason=end_reason,
                        team=team,
                        opponent_team=opponent_team,
                        include_pressure=include_pressure
                    )

                    buildups.append(buildup_data)

                # Reset for next buildup (regardless of extraction)
                buildup_active = False
                buildup_start_idx = None
                buildup_events = []

    # Handle unclosed buildup at end of sequence
    # The buildup extends to the end of the sequence, and we use the sequence's end_reason
    # This captures buildups that failed to progress (lost possession before crossing)
    if buildup_active and len(buildup_events) > 1:
        n_passes = sum(1 for e in buildup_events if e['type_name'] == 'Pass')

        if n_passes >= 2:
            buildup_data = _compute_buildup_metrics(
                events=buildup_events,
                sequence_id=sequence_id,
                start_idx=buildup_start_idx,
                end_idx=len(possession_seq) - 1,
                end_reason=sequence_end_reason,  # Use sequence's end reason (why possession ended)
                team=team,
                opponent_team=opponent_team,
                include_pressure=include_pressure
            )
            buildups.append(buildup_data)

    return buildups


def _check_buildup_start(event: pd.Series, team: str) -> bool:
    """
    Check if event satisfies buildup start condition.

    Buildup starts when:
      - Event type in [Ball Recovery, Clearance, Goal Keeper]
      - Event x < 33.33 (first third)
      - Team possession
    """
    if event['team'] != team:
        return False

    event_type = event['type_name']
    event_x = event['x']

    # Check event type
    valid_start_types = ['Ball Recovery', 'Clearance', 'Goal Keeper']
    if event_type not in valid_start_types:
        return False

    # Check position (first third only)
    if pd.isna(event_x) or event_x >= 33.33:
        return False

    return True


def _check_buildup_end(
    events: List[pd.Series],
    current_event: pd.Series,
    team: str
) -> Tuple[bool, str]:
    """
    Check if buildup should end.

    Buildup ends when ANY of:
      1. x > 50 (crossed halfway) - only team's passes count
      2. Shot taken
      3. Dispossessed/Miscontrol (ball lost)
      4. Duration > 60 seconds
    """
    event_type = current_event['type_name']
    event_x = current_event['x']
    event_team = current_event['team']

    # Condition 1: Crossed halfway line (only count team's progression, not opponent interceptions)
    if event_team == team and pd.notna(event_x) and event_x > 50:
        return True, 'crossed_halfway'

    # Condition 2: Shot taken (team's shot ends buildup)
    if event_team == team and event_type == 'Shot':
        return True, 'shot_taken'

    # Condition 3: Lost possession (team's events only)
    if event_team == team and event_type in ['Dispossessed', 'Miscontrol']:
        return True, 'lost_possession'

    # Condition 4: Extended duration (over 60 seconds)
    if len(events) > 1:
        first_time = events[0].get('timestamp', '00:00:00.000')
        last_time = events[-1].get('timestamp', '00:00:00.000')

        try:
            from datetime import datetime
            t1 = datetime.strptime(first_time, '%H:%M:%S.%f')
            t2 = datetime.strptime(last_time, '%H:%M:%S.%f')
            duration_sec = (t2 - t1).total_seconds()

            if duration_sec > 60:
                return True, 'extended_duration'
        except:
            pass

    return False, None


def _compute_buildup_metrics(
    events: List[pd.Series],
    sequence_id: int,
    start_idx: int,
    end_idx: int,
    end_reason: str,
    team: str,
    opponent_team: str = None,
    include_pressure: bool = False
) -> Dict:
    """
    Compute comprehensive buildup metrics.

    Args:
        events: List of events in buildup
        sequence_id: Parent sequence ID
        start_idx: Start event index in sequence
        end_idx: End event index in sequence
        end_reason: Why buildup ended
        team: Team name
        opponent_team: Opponent team
        include_pressure: Calculate pressure metrics

    Returns:
        Dict with buildup metrics
    """
    # Convert to DataFrame for easier analysis
    buildup_df = pd.DataFrame(events)

    # STRUCTURAL METRICS
    n_events = len(buildup_df)
    n_passes = len(buildup_df[buildup_df['type_name'] == 'Pass'])
    n_carries = len(buildup_df[buildup_df['type_name'] == 'Carry'])

    # POSITION METRICS
    start_x = buildup_df.iloc[0]['x'] if pd.notna(buildup_df.iloc[0]['x']) else None
    end_x = buildup_df.iloc[-1]['x'] if pd.notna(buildup_df.iloc[-1]['x']) else None
    max_x = buildup_df['x'].max()

    # Distance traveled (horizontal only)
    x_values = buildup_df['x'].dropna()
    if len(x_values) > 1:
        distance_traveled = float(x_values.iloc[-1] - x_values.iloc[0])
    else:
        distance_traveled = 0.0

    # Check if crossed halfway
    crossed_halfway = any(buildup_df['x'] > 50)

    # Zone tracking
    start_zone = _get_zone_name(start_x)
    end_zone = _get_zone_name(end_x)

    # TEMPO METRICS
    first_time = buildup_df.iloc[0].get('timestamp', '00:00:00.000')
    last_time = buildup_df.iloc[-1].get('timestamp', '00:00:00.000')

    try:
        from datetime import datetime
        t1 = datetime.strptime(first_time, '%H:%M:%S.%f')
        t2 = datetime.strptime(last_time, '%H:%M:%S.%f')
        duration_sec = (t2 - t1).total_seconds()
    except:
        duration_sec = 0.0

    passes_per_sec = n_passes / duration_sec if duration_sec > 0 else 0.0
    avg_x_per_event = distance_traveled / n_events if n_events > 0 else 0.0

    # PLAYER INVOLVEMENT
    n_players = buildup_df['player'].nunique()
    positions = buildup_df['position'].dropna().unique()
    defenders = len([p for p in positions if p in ['Center Back', 'Right Back', 'Left Back']])
    midfielders = len([p for p in positions if 'Midfield' in str(p)])

    # SUCCESS CONDITION
    is_successful = _check_buildup_success(
        crossed_halfway=crossed_halfway,
        end_reason=end_reason,
        n_passes=n_passes
    )

    # PRESSURE METRICS (optional) - using pressure360 (carry-based, duration-weighted)
    mean_pressure = None
    max_pressure = None
    pressure_intensity = None

    if include_pressure:
        try:
            from .pressure360 import calculate_sequence_pressure
            pressure_data = calculate_sequence_pressure(events, team=team)
            mean_pressure = pressure_data['mean_pressure']
            max_pressure = pressure_data['max_pressure']
            pressure_intensity = pressure_data['intensity_level']
        except Exception as e:
            # Silently skip if pressure calculation fails
            pass

    # Get actual event index from first event (StatsBomb event index)
    first_event_idx = events[0].get('index') if len(events) > 0 else None

    # BUILD RESULT DICT
    buildup_metrics = {
        # Identifiers
        'sequence_id': sequence_id,
        'start_idx': start_idx,
        'start_event_index': start_idx,
        'event_index': first_event_idx,
        'end_event_index': end_idx,

        # Location
        'start_zone': start_zone,
        'end_zone': end_zone,
        'start_x': float(start_x) if start_x is not None else None,
        'end_x': float(end_x) if end_x is not None else None,
        'max_x_reached': float(max_x) if pd.notna(max_x) else None,
        'distance_traveled': float(distance_traveled),
        'crossed_halfway': bool(crossed_halfway),

        # Composition
        'n_events': int(n_events),
        'n_passes': int(n_passes),
        'n_carries': int(n_carries),
        'n_players_involved': int(n_players),
        'defenders_involved': int(defenders),
        'midfielders_involved': int(midfielders),

        # Tempo & Control
        'duration_sec': round(duration_sec, 2),
        'passes_per_second': round(passes_per_sec, 3),
        'avg_x_per_event': round(avg_x_per_event, 2),

        # Pressure Context
        'mean_pressure': round(mean_pressure, 3) if mean_pressure is not None else None,
        'max_pressure': round(max_pressure, 3) if max_pressure is not None else None,
        'pressure_intensity': pressure_intensity,

        # Outcome
        'end_reason': end_reason,
        'is_successful': bool(is_successful),
    }

    return buildup_metrics


def _check_buildup_success(
    crossed_halfway: bool,
    end_reason: str,
    n_passes: int = None
) -> bool:
    """
    Check if buildup was successful.

    Successful if accomplished the buildup objective:
    - Reached opponent half (x > 50) AND maintained possession
    - OR took a shot

    Failed if:
    - Lost possession (dispossessed, miscontrol, foul committed, unsuccessful pass)
    - Did not progress despite having time (extended_duration without progression)
    """
    # End reasons that indicate possession loss = FAILURE
    if end_reason in ['lost_possession', 'dispossessed', 'miscontrol', 'foul_committed', 'unsuccessful_pass']:
        return False

    # End reasons that indicate success
    if end_reason == 'crossed_halfway' or end_reason == 'shot_taken':
        return crossed_halfway or end_reason == 'shot_taken'

    # Gap in play (stoppage) = FAILURE (didn't complete buildup)
    if end_reason == 'gap_in_play':
        return False

    # Extended duration without crossing = FAILURE
    if end_reason == 'extended_duration':
        return crossed_halfway  # Only success if it did eventually cross

    # match_end = SUCCESS if crossed halfway before it ended
    if end_reason == 'match_end':
        return crossed_halfway

    # Foul Won = SUCCESS (gained possession, buildup continues)
    if end_reason == 'foul_won':
        return True

    # Default: unsuccessful
    return False


def _get_zone_name(x: float) -> str:
    """Get zone name from x coordinate."""
    if pd.isna(x):
        return 'unknown'
    elif x < 33.33:
        return 'first_third'
    elif x < 66.67:
        return 'second_third'
    else:
        return 'third_third'


def buildups_to_dataframe(buildups: List[Dict]) -> pd.DataFrame:
    """
    Convert buildup list to DataFrame for easier analysis.

    Args:
        buildups: List of buildup dicts

    Returns:
        DataFrame with one row per buildup
    """
    if not buildups:
        return pd.DataFrame()

    return pd.DataFrame(buildups)


def summarize_buildups(buildups: List[Dict]) -> Dict:
    """
    Generate summary statistics for all buildups.

    Args:
        buildups: List of buildup dicts

    Returns:
        Dict with aggregate statistics
    """
    if not buildups:
        return {}

    df = buildups_to_dataframe(buildups)

    # Pressure-stratified success rates
    low_pressure = df[df['mean_pressure'] < 0.2]
    medium_pressure = df[(df['mean_pressure'] >= 0.2) & (df['mean_pressure'] < 0.6)]
    high_pressure = df[df['mean_pressure'] >= 0.6]

    success_rate_low = f"{100 * low_pressure['is_successful'].mean():.1f}%" if len(low_pressure) > 0 else "N/A"
    success_rate_medium = f"{100 * medium_pressure['is_successful'].mean():.1f}%" if len(medium_pressure) > 0 else "N/A"
    success_rate_high = f"{100 * high_pressure['is_successful'].mean():.1f}%" if len(high_pressure) > 0 else "N/A"

    return {
        'total_buildups': len(buildups),
        'successful_buildups': df['is_successful'].sum(),
        'success_rate': f"{100 * df['is_successful'].mean():.1f}%",
        'avg_duration_sec': round(df['duration_sec'].mean(), 2),
        'avg_passes': round(df['n_passes'].mean(), 1),
        'avg_distance_m': round(df['distance_traveled'].mean(), 1),
        'avg_pressure': round(df['mean_pressure'].mean(), 3) if df['mean_pressure'].notna().any() else None,
        'success_rate_low_pressure': success_rate_low,
        'success_rate_medium_pressure': success_rate_medium,
        'success_rate_high_pressure': success_rate_high,
        'buildups_by_end_reason': df['end_reason'].value_counts().to_dict(),
    }
