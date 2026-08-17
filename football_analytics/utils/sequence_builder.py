"""
Possession sequence builder using StatsBomb possession tracking.

Uses StatsBomb's built-in possession and possession_team fields
to extract sequences instead of manual possession change detection.

Each sequence:
- Contains all events (both teams) during a possession for complete context
- Is identified by StatsBomb's possession sequence number
- Belongs to the specified team (possession_team field)
"""

import pandas as pd
from .pitch_zones import get_zone


def build_sequences(events_df: pd.DataFrame, team: str) -> list:
    """
    Build possession sequences for a team using StatsBomb possession data.

    Groups events by possession sequence and filters for sequences where
    the specified team has possession. Includes ALL events during each
    possession for context.

    Args:
        events_df: Match events DataFrame from load_match_events
        team: Team name to extract sequences for

    Returns:
        List of DataFrames, each representing one possession sequence with:
        - All events during the team's possession (including opponent events)
        - sequence_id, start_zone, end_zone, n_passes, n_carries, etc.
    """
    if len(events_df) == 0:
        return []

    sequences = []
    sequence_id = 0

    # Get unique possession sequences for this team
    team_possessions = events_df[events_df['possession_team'] == team]
    if len(team_possessions) == 0:
        return []

    unique_possession_nums = team_possessions['possession'].unique()

    # For each possession sequence, collect all events (both teams)
    for poss_num in sorted(unique_possession_nums):
        # Get all events in this possession (both teams)
        poss_events = events_df[events_df['possession'] == poss_num]

        if len(poss_events) > 0:
            seq_df = _finalize_sequence(poss_events, sequence_id, team)
            sequences.append(seq_df)
            sequence_id += 1

    return sequences


def _finalize_sequence(events_df: pd.DataFrame, sequence_id: int, team: str) -> pd.DataFrame:
    """
    Create a finalized sequence DataFrame with metadata.

    Args:
        events_df: DataFrame of all events in this possession sequence
        sequence_id: Sequence identifier
        team: Target team name

    Returns:
        DataFrame with sequence events + metadata columns
    """
    # Count only target team's actions
    team_events = events_df[events_df['team'] == team]
    n_passes = len(team_events[team_events['type_name'] == 'Pass'])
    n_carries = len(team_events[team_events['type_name'] == 'Carry'])

    # Position tracking (use target team's events)
    team_with_x = team_events[team_events['x'].notna()]
    if len(team_with_x) > 0:
        start_x = team_with_x.iloc[0]['x']
        end_x = team_with_x.iloc[-1]['x']
    else:
        start_x = None
        end_x = None

    start_zone = get_zone(start_x) if pd.notna(start_x) else 'unknown'
    end_zone = get_zone(end_x) if pd.notna(end_x) else 'unknown'

    reached_f3 = any(team_events['x'] > 80) if len(team_events) > 0 else False

    # Duration: from first to last event in sequence
    first_time = events_df.iloc[0]['timestamp']
    last_time = events_df.iloc[-1]['timestamp']
    try:
        from datetime import datetime
        t1 = datetime.strptime(first_time, '%H:%M:%S.%f')
        t2 = datetime.strptime(last_time, '%H:%M:%S.%f')
        duration_sec = (t2 - t1).total_seconds()
    except:
        duration_sec = 0.0

    # Determine end reason from how possession ended
    end_reason = 'unknown'
    last_team_event = team_events.iloc[-1] if len(team_events) > 0 else None
    if last_team_event is not None:
        event_type = last_team_event['type_name']
        if event_type in ['Dispossessed', 'Miscontrol', 'Foul Committed']:
            end_reason = event_type.lower().replace(' ', '_')
        elif event_type == 'Pass':
            if pd.notna(last_team_event.get('pass_outcome_name')):
                end_reason = f"pass_{last_team_event['pass_outcome_name'].lower()}"
            else:
                end_reason = 'pass'
        elif event_type == 'Shot':
            end_reason = 'shot'
        else:
            end_reason = event_type.lower().replace(' ', '_')

    # Check if sequence crossed halfway (reached opponent half)
    crossed_halfway = any(team_events['x'] > 50) if len(team_events) > 0 else False

    # Add metadata columns
    result = events_df.copy()
    result['sequence_id'] = sequence_id
    result['start_zone'] = start_zone
    result['end_zone'] = end_zone
    result['n_passes'] = n_passes
    result['n_carries'] = n_carries
    result['reached_final_third'] = reached_f3
    result['crossed_halfway'] = crossed_halfway
    result['duration_sec'] = duration_sec
    result['end_reason'] = end_reason

    return result
