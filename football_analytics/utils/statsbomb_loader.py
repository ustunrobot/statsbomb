"""
StatsBomb data loader and normalizer.

Handles reading JSON event files from local filesystem,
normalizing nested structures into flat DataFrames.
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np


def get_all_teams(data_dir: str = "data") -> list:
    """
    Get all team folder names under data/teams/.

    Returns:
        Sorted list of team names (folder names).
    """
    teams_dir = Path(data_dir) / "teams"
    teams = sorted([d.name for d in teams_dir.iterdir() if d.is_dir()])
    return teams


def get_team_match_files(team: str, data_dir: str = "data", week: int = None) -> list:
    """
    Get match JSON files for a team, optionally filtered by week.

    Args:
        team: Team name (folder name under data/teams/)
        data_dir: Base data directory path
        week: Optional week number to filter (e.g., 15 for Week15_*.json)

    Returns:
        Sorted list of Path objects to .json files.
    """
    team_dir = Path(data_dir) / "teams" / team

    if week:
        # Filter by week pattern (e.g., Week15_)
        files = sorted([f for f in team_dir.glob(f"Week{week}_*.json")])
    else:
        files = sorted([f for f in team_dir.glob("*.json")])

    return files


def load_match_events(filepath: str | Path) -> pd.DataFrame:
    """
    Load and normalize a single match JSON file.

    Converts nested StatsBomb JSON structure into flat DataFrame:
    - location [x, y] → x, y float columns
    - Nested dicts flattened: pass_length, pass_end_x, pass_end_y,
      pass_recipient_name, pass_height_name, carry_end_x, carry_end_y, etc.

    Args:
        filepath: Path to match JSON file

    Returns:
        Normalized DataFrame with columns:
            - Core: id, index, timestamp, period, minute, second, team,
                    type_name, player, position
            - Location: x, y
            - Pass fields: pass_length, pass_angle, pass_end_x, pass_end_y,
                          pass_recipient_name, pass_technique_name, pass_height_name
            - Carry fields: carry_end_x, carry_end_y
            - Other: under_pressure, match_id, source_file
    """
    filepath = Path(filepath)

    # Load JSON (dict of event UUIDs)
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Convert dict to list sorted by index
    events_list = list(data.values())
    events_list = sorted(events_list, key=lambda e: e.get('index', 0))

    # Normalize each event
    normalized = []
    for event in events_list:
        row = {
            'id': event.get('id'),
            'index': event.get('index'),
            'timestamp': event.get('timestamp'),
            'period': event.get('period'),
            'minute': event.get('minute'),
            'second': event.get('second'),
            'type_name': event.get('type', {}).get('name'),
            'team': event.get('team', {}).get('name'),
            'player': event.get('player', {}).get('name'),
            'position': event.get('position', {}).get('name'),
            'play_pattern': event.get('play_pattern', {}).get('name') if isinstance(event.get('play_pattern'), dict) else event.get('play_pattern'),
            'under_pressure': event.get('under_pressure'),
            'possession': event.get('possession'),
            'possession_team': event.get('possession_team', {}).get('name'),
            'duration': event.get('duration'),
            'match_id': event.get('match_id'),
            'recipient': event.get('pass', {}).get('recipient', {}).get('name'),
            'source_file': filepath.name,
        }

        # Location: [x, y]
        location = event.get('location')
        if location and len(location) >= 2:
            row['x'] = float(location[0])
            row['y'] = float(location[1])
        else:
            row['x'] = np.nan
            row['y'] = np.nan

        # Pass fields
        pass_data = event.get('pass', {})
        if pass_data:
            row['pass_length'] = pass_data.get('length')
            row['pass_angle'] = pass_data.get('angle')
            end_loc = pass_data.get('end_location')
            if end_loc and len(end_loc) >= 2:
                row['pass_end_x'] = float(end_loc[0])
                row['pass_end_y'] = float(end_loc[1])
            else:
                row['pass_end_x'] = np.nan
                row['pass_end_y'] = np.nan
            row['pass_recipient_name'] = pass_data.get('recipient', {}).get('name')
            row['pass_technique_name'] = pass_data.get('technique', {}).get('name')
            row['pass_height_name'] = pass_data.get('height', {}).get('name')
            row['pass_type_name'] = pass_data.get('type', {}).get('name')
            row['pass_outcome_name'] = pass_data.get('outcome', {}).get('name')
            row['pass_success_probability'] = pass_data.get('pass_success_probability')
        else:
            row['pass_length'] = np.nan
            row['pass_angle'] = np.nan
            row['pass_end_x'] = np.nan
            row['pass_end_y'] = np.nan
            row['pass_recipient_name'] = None
            row['pass_technique_name'] = None
            row['pass_height_name'] = None
            row['pass_type_name'] = None
            row['pass_outcome_name'] = None
            row['pass_success_probability'] = np.nan

        # Carry fields
        carry_data = event.get('carry', {})
        if carry_data:
            end_loc = carry_data.get('end_location')
            if end_loc and len(end_loc) >= 2:
                row['carry_end_x'] = float(end_loc[0])
                row['carry_end_y'] = float(end_loc[1])
            else:
                row['carry_end_x'] = np.nan
                row['carry_end_y'] = np.nan
        else:
            row['carry_end_x'] = np.nan
            row['carry_end_y'] = np.nan

        # Goalkeeper fields
        gk_data = event.get('goalkeeper', {})
        if gk_data:
            end_loc = gk_data.get('end_location')
            if end_loc and len(end_loc) >= 2:
                row['gk_end_x'] = float(end_loc[0])
                row['gk_end_y'] = float(end_loc[1])
            else:
                row['gk_end_x'] = np.nan
                row['gk_end_y'] = np.nan
            row['gk_type_name'] = gk_data.get('type', {}).get('name')
            row['gk_position_name'] = gk_data.get('position', {}).get('name')
        else:
            row['gk_end_x'] = np.nan
            row['gk_end_y'] = np.nan
            row['gk_type_name'] = None
            row['gk_position_name'] = None

        # Defensive responsibility fields (for pressure analysis)
        def_resp = event.get('defensive_responsibility')
        row['defensive_responsibility'] = def_resp

        normalized.append(row)

    df = pd.DataFrame(normalized)
    return df


def load_team_season(team: str, data_dir: str = "data", week: int = None) -> pd.DataFrame:
    """
    Load all matches for a team into a single DataFrame.

    Args:
        team: Team name
        data_dir: Base data directory
        week: Optional week number to filter (e.g., 15 for Week15_*.json)

    Returns:
        Concatenated DataFrame of all team's events with reset index.
    """
    files = get_team_match_files(team, data_dir, week=week)
    dfs = []

    for filepath in files:
        try:
            df = load_match_events(filepath)
            dfs.append(df)
        except Exception as e:
            print(f"Warning: Failed to load {filepath}: {e}")

    if dfs:
        result = pd.concat(dfs, ignore_index=True)
        return result
    else:
        return pd.DataFrame()


def load_full_league(data_dir: str = "data", teams: list = None, week: int = None) -> dict:
    """
    Load all teams (or subset) into a dictionary of DataFrames.

    Args:
        data_dir: Base data directory
        teams: List of team names to load. If None, loads all teams.
        week: Optional week number to filter (e.g., 15 for Week15_*.json)

    Returns:
        Dict mapping team name → events DataFrame
    """
    if teams is None:
        teams = get_all_teams(data_dir)

    league_data = {}

    for team in teams:
        files = get_team_match_files(team, data_dir, week=week)
        print(f"Loading {team}... {len(files)} matches found")
        league_data[team] = load_team_season(team, data_dir, week=week)

    return league_data


def get_match_teams(events_df: pd.DataFrame) -> tuple:
    """
    Identify home and away teams from an events DataFrame.

    Returns:
        Tuple (home_team, away_team) — determined by team column values.
        Note: Assumes events_df is from a single match.
    """
    teams = events_df['team'].dropna().unique()
    if len(teams) >= 2:
        return tuple(sorted(teams))[:2]
    elif len(teams) == 1:
        return (teams[0], None)
    else:
        return (None, None)
