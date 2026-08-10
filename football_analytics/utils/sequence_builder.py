"""
Possession sequence builder.

Sequences are continuous stretches of possession that end on:
- Possession loss (incomplete pass, turnover, tackle)
- Clearance
- Shot
- Foul
- Out of play

Each sequence is tagged with tactical metadata for analysis.
"""

import pandas as pd
from typing import list
from .pitch_zones import get_zone


def build_sequences(events_df: pd.DataFrame, team: str) -> list:
    """
    Build possession sequences for a team.

    Each sequence is a continuous possession ending on loss/shot/clearance/foul.
    Sequences are tagged with:
    - sequence_id: Unique identifier
    - start_zone: Defensive, middle, or final
    - end_zone: Zone where possession ended
    - n_passes: Number of completed passes
    - n_carries: Number of carries
    - reached_final_third: Boolean if sequence crossed x=80
    - duration_sec: Time span of sequence

    Args:
        events_df: Match events DataFrame from load_match_events
        team: Team name to extract sequences for

    Returns:
        List of DataFrames, each representing one possession sequence.
    """
    sequences = []

    # Filter to team's events
    team_events = events_df[events_df['team'] == team].copy()

    if len(team_events) == 0:
        return sequences

    # Group by possession_id if available, or build manually
    # For now, build sequences based on possession changes
    current_sequence = []
    sequence_id = 0

    for idx, event in team_events.iterrows():
        event_type = event['type_name']

        # Add event to current sequence
        current_sequence.append(event)

        # Check if sequence should end
        should_end = False
        end_reason = None

        if event_type == 'Dispossessed':
            should_end = True
            end_reason = 'dispossessed'
        elif event_type == 'Miscontrol':
            should_end = True
            end_reason = 'miscontrol'
        elif event_type == 'Pass' and pd.notna(event['pass_type_name']):
            # Unsuccessful pass ends sequence
            pass_outcome = event.get('pass_type_name', '')
            if 'Unsuccessful' in str(pass_outcome):
                should_end = True
                end_reason = 'unsuccessful_pass'
        elif event_type in ['Clearance', 'Shot', 'Foul Committed']:
            should_end = True
            end_reason = event_type.lower()
        elif event_type == 'Out':
            should_end = True
            end_reason = 'out_of_play'

        # Build sequence if ending
        if should_end and len(current_sequence) > 0:
            seq_df = pd.DataFrame(current_sequence)

            # Calculate metrics
            n_passes = len(seq_df[seq_df['type_name'] == 'Pass'])
            n_carries = len(seq_df[seq_df['type_name'] == 'Carry'])

            start_x = current_sequence[0].get('x')
            end_x = current_sequence[-1].get('x')
            start_zone = get_zone(start_x) if pd.notna(start_x) else 'unknown'
            end_zone = get_zone(end_x) if pd.notna(end_x) else 'unknown'

            reached_f3 = any(seq_df['x'] > 80)

            # Duration
            first_time = current_sequence[0].get('timestamp', '00:00:00.000')
            last_time = current_sequence[-1].get('timestamp', '00:00:00.000')
            try:
                from datetime import datetime
                t1 = datetime.strptime(first_time, '%H:%M:%S.%f')
                t2 = datetime.strptime(last_time, '%H:%M:%S.%f')
                duration_sec = (t2 - t1).total_seconds()
            except:
                duration_sec = 0.0

            # Add metadata
            seq_df['sequence_id'] = sequence_id
            seq_df['start_zone'] = start_zone
            seq_df['end_zone'] = end_zone
            seq_df['n_passes'] = n_passes
            seq_df['n_carries'] = n_carries
            seq_df['reached_final_third'] = reached_f3
            seq_df['duration_sec'] = duration_sec
            seq_df['end_reason'] = end_reason

            sequences.append(seq_df)
            sequence_id += 1
            current_sequence = []

    return sequences
