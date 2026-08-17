"""
Buildup sequence finder using refined start/end conditions.

Detects buildup sequences based on:
- Start conditions: GK involvement, goal kicks, free kicks
- End conditions: Crosses halfway, possession loss, long balls
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from .pressure360 import calculate_sequence_pressure


def find_buildups(events_df: pd.DataFrame, team: str) -> List[Dict]:
    """
    Find buildup sequences in match events.

    Args:
        events_df: DataFrame with match events (from statsbomb_loader)
        team: Team name to analyze

    Returns:
        List of buildup dicts with:
        - events: list of event rows
        - n_passes: count of passes
        - outcome: 'success', 'fail', or 'long_ball'
        - mean_pressure: pressure intensity
        - intensity_level: 'LOW', 'MEDIUM', 'HIGH', 'EXTREME'
    """
    buildups = []
    buildup_events = []
    buildup_active = False
    buildup_gk_name = ""
    n_passes_in_buildup = 0  # Track passes during buildup

    # Fast iteration using itertuples instead of iterrows (5-10x faster)
    for row in events_df.itertuples(index=False, name='Event'):
        event_type = row.type_name
        event_team = row.team
        possession_team = row.possession_team
        
        # CHECK START CONDITIONS
        if not buildup_active and event_team == team and possession_team == team:
            if _check_buildup_start(row):
                buildup_active = True
                buildup_events = [row]
                n_passes_in_buildup = 0
                buildup_gk_name = row.player        
                continue  # Skip to next event after starting buildup

        # COLLECT EVENTS DURING BUILDUP
        if buildup_active:
            # Collect both team events 
            buildup_events.append(row)
            if event_team == team and event_type == 'Pass':
                n_passes_in_buildup += 1

            # CHECK END CONDITIONS
            should_end, outcome = _check_buildup_end(
                current_event=row,
                buildup_events=buildup_events,
                team=team,
            )

            if should_end:
                # include all fails  + #pass > 3, 
                if outcome != 'half_end' and (outcome == 'fail' or n_passes_in_buildup >= 3):
                    buildup_data = _compute_buildup_data(
                        events=buildup_events,
                        outcome=outcome,                        
                        team=team,
                        gk=buildup_gk_name
                    )                    
                    buildups.append(buildup_data)

                buildup_active = False
                buildup_events = []
                n_passes_in_buildup = 0

    # Handle unclosed buildup at end of match
    if buildup_active and len(buildup_events) > 0 and n_passes_in_buildup >= 3:
        buildup_data = _compute_buildup_data(
            events=buildup_events,
            outcome='success',
            team=team,
            gk=buildup_gk_name
        )
        buildups.append(buildup_data)

    return buildups


def _check_buildup_start(event) -> bool:
    """
    Check if event satisfies buildup start condition.

    Start conditions (all in defensive third, x < 30):
    1. Ball Receipt or Ball Recovery + position = Goalkeeper
    2. Pass + play_pattern = "From Goal Kick" + pass_length < 40
    3. Pass + play_pattern = "From Free Kick" + pass_length < 40
    """
    event_type = event.type_name
    position = event.position
    play_pattern = event.play_pattern
    x = event.x
    pass_length = event.pass_length

    if event_type == 'Pass' and position == 'Goalkeeper' and pass_length < 40:
        return True

    return False



    # All conditions require x < 30 (defensive third)
    if pd.notna(x) and x >= 30:
        return False

    # Condition 1: GK involvement
    if event_type in ['Ball Receipt*', 'Ball Recovery', 'Pass']:
        if position == 'Goalkeeper':
            return True

    # Condition 2: From Goal Kick (short pass < 40m)
    if event_type == 'Pass' and play_pattern == 'From Goal Kick':
        if pd.notna(pass_length) and pass_length < 40:
            return True

    # Condition 3: From Free Kick (short pass < 40m)
    if event_type == 'Pass' and play_pattern == 'From Free Kick':
        if pd.notna(pass_length) and pass_length < 40:
            return True

    return False


def _check_buildup_end(
    current_event,
    buildup_events: List,
    team: str,
) -> tuple:
    """
    Check if buildup should end and return outcome.

    End conditions:
    1. x > 60 and passes >= 3 and possession held: success
    2. Possession changed: fail
    3. Pass length > 40: long_ball
    """
    event_type = current_event.type_name
    event_team = current_event.team
    x = current_event.x
    possession_team = current_event.possession_team
    pass_length = current_event.pass_length

    if event_type == 'Half End':
        return True, 'half_end'
    
    # Condition 1: Possession changed
    if possession_team != team:
        return True, 'fail'

    # Condition 2: Team of interest must be the one in possession
    if event_team != team:
        return False, None  # Only consider events from the team of interest

    # if we are here, the team is still in possession and the event is from the team of interest
    # Condition 3: Crossed halfway 
    if pd.notna(x) and x > 60:
        return True, 'success'

    # Condition 4: Long pass (> 40 meters)
    # any long pass terminates the buildup sequence
    if event_type == 'Pass' and pd.notna(pass_length) and pass_length > 40:
        return True, 'long_ball'

    return False, None


def _compute_buildup_data(
    events: List,
    outcome: str,
    team: str,
    gk: str
) -> Dict:
    """
    Compute buildup metrics and return dict.

    Args:
        events: List of event rows in buildup
        outcome: 'success', 'fail', 'long_ball', or 'incomplete'
        team: Team name

    Returns:
        Dict with buildup data
    """
    n_events = len(events)
    if n_events == 0:
        return {}

    # Fast metrics calculation (avoid DataFrame conversion)
    n_passes = sum(1 for e in events if e.type_name == 'Pass')
    intensity_level = None

    try:
        # Convert namedtuples to dicts for pressure calculation
        events_as_dicts = [event._asdict() if hasattr(event, '_asdict') else dict(event) for event in events]
        pressure_data = calculate_sequence_pressure(events_as_dicts, team=team)
        intensity_level = pressure_data.get('intensity_level')
    except Exception as e:
        print(f"  Warning: Pressure calculation failed for buildup: {e}")
        

    # Get event indices
    first_event_idx = events[0].index if hasattr(events[0], 'index') else None
    last_event_idx = events[-1].index if hasattr(events[-1], 'index') else None

    return {
        'n_events': int(n_events),
        'n_passes': int(n_passes),
        'outcome': outcome,
        'intensity_level': intensity_level,
        'first_event_index': first_event_idx,
        'last_event_index': last_event_idx,
        'gk_name': gk,
        'events': events,
    }


def summarize_buildups(buildups: List[Dict]) -> Dict:
    """
    Generate summary statistics for all buildups.

    Args:
        buildups: List of buildup dicts

    Returns:
        Dict with aggregate statistics including outcome ratios by pressure intensity
    """
    if not buildups:
        return {}

    df = pd.DataFrame([{k: v for k, v in b.items() if k != 'events'} for b in buildups])

    # Outcome counts
    outcome_counts = df['outcome'].value_counts().to_dict()

    # Outcome ratios by intensity level
    # LOW pressure intensity
    low_intensity = df[df['intensity_level'] == 'LOW']
    low_pres_success = f"{100 * len(low_intensity[low_intensity['outcome'] == 'success']) / len(low_intensity):.1f}%" if len(low_intensity) > 0 else "N/A"
    low_pres_long = f"{100 * len(low_intensity[low_intensity['outcome'] == 'long_ball']) / len(low_intensity):.1f}%" if len(low_intensity) > 0 else "N/A"

    # MEDIUM pressure intensity
    medium_intensity = df[df['intensity_level'] == 'MEDIUM']
    mid_pres_success = f"{100 * len(medium_intensity[medium_intensity['outcome'] == 'success']) / len(medium_intensity):.1f}%" if len(medium_intensity) > 0 else "N/A"
    mid_pres_long = f"{100 * len(medium_intensity[medium_intensity['outcome'] == 'long_ball']) / len(medium_intensity):.1f}%" if len(medium_intensity) > 0 else "N/A"

    # EXTREME pressure intensity (high)
    extreme_intensity = df[df['intensity_level'] == 'EXTREME']
    high_pres_success = f"{100 * len(extreme_intensity[extreme_intensity['outcome'] == 'success']) / len(extreme_intensity):.1f}%" if len(extreme_intensity) > 0 else "N/A"
    high_pres_long = f"{100 * len(extreme_intensity[extreme_intensity['outcome'] == 'long_ball']) / len(extreme_intensity):.1f}%" if len(extreme_intensity) > 0 else "N/A"

    return {
        '#buildups': len(buildups),
        '#successful': outcome_counts.get('success', 0),
        '#failed': outcome_counts.get('fail', 0),
        '#long_ball': outcome_counts.get('long_ball', 0),
        '#succ_rate': f"{100 * outcome_counts.get('success', 0) / len(buildups):.1f}%" if len(buildups) > 0 else "0.0%",
        'lpres_succ': low_pres_success,
        'lpres_long': low_pres_long,
        'mpres_succ': mid_pres_success,
        'mpres_long': mid_pres_long,
        'hpres_succ': high_pres_success,
        'hpres_long': high_pres_long,
    }


def export_buildups_to_csv(buildups: List[Dict], output_path: str = 'buildups_export.csv') -> None:
    """
    Export buildup events to CSV file with carry distance calculations.

    Args:
        buildups: List of buildup dicts with 'events' field
        output_path: Path to save CSV file

    Columns:
        matchid, buildup_no, index, type_name, position, x, y,
        end_x, end_y, euclidean_distance, vertical_distance (for Carry events)
    """
    rows = []

    for buildup_no, buildup in enumerate(buildups, start=1):
        events = buildup.get('events', [])

        # Extract match_id from first event
        match_id = None
        if events:
            first_event = events[0]
            match_id = first_event.get('match_id') if isinstance(first_event, dict) else getattr(first_event, 'match_id', None)

        for event in events:
            # Handle both dict and namedtuple event access
            event_index = event.get('index') if isinstance(event, dict) else getattr(event, 'index', None)
            event_type = event.get('type_name') if isinstance(event, dict) else getattr(event, 'type_name', None)
            position = event.get('position') if isinstance(event, dict) else getattr(event, 'position', None)
            x = event.get('x') if isinstance(event, dict) else getattr(event, 'x', None)
            y = event.get('y') if isinstance(event, dict) else getattr(event, 'y', None)
            team = event.get('team') if isinstance(event, dict) else getattr(event, 'team', None)

            row = {
                'matchid': match_id,
                'team': team,
                'buildup_no': buildup_no,
                'index': event_index,
                'type_name': event_type,
                'position': position,
                'outcome': buildup.get("outcome"),
                'x': x,
                'y': y,
                'end_x': None,
                'end_y': None,
                'euclidean_distance': None,
                'vertical_distance': None,
            }

            # For Carry events, calculate distances
            if event_type == 'Carry':
                end_x = event.get('carry_end_x') if isinstance(event, dict) else getattr(event, 'carry_end_x', None)
                end_y = event.get('carry_end_y') if isinstance(event, dict) else getattr(event, 'carry_end_y', None)

                if pd.notna(x) and pd.notna(y) and pd.notna(end_x) and pd.notna(end_y):
                    row['end_x'] = end_x
                    row['end_y'] = end_y
                    row['euclidean_distance'] = np.sqrt((end_x - x) ** 2 + (end_y - y) ** 2)
                    row['vertical_distance'] = abs(end_x - x)

            rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"✓ Exported {len(rows)} events from {len(buildups)} buildups to: {output_path}")
