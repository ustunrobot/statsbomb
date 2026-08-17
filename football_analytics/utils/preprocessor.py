"""
Season data preprocessing utilities.

Combines and caches match events per team for fast season-wide operations.
"""

from pathlib import Path
from utils.statsbomb_loader import load_team_season, get_all_teams


def preprocess_team_seasons(data_dir: str = "data", teams: list = None) -> None:
    """
    One-time preprocessing: combine all season games per team and save.

    Creates a combined events file per team for fast season-wide operations.
    Saves as CSV in data/teams/{team}/season_events.csv

    Args:
        data_dir: Base data directory
        teams: List of team names. If None, processes all teams.
    """
    if teams is None:
        teams = get_all_teams(data_dir)

    print(f"Preprocessing season data for {len(teams)} teams...")

    for team in teams:
        print(f"  {team}...", end=" ", flush=True)

        team_events = load_team_season(team, data_dir)

        if len(team_events) > 0:
            # Save as CSV for fast I/O
            team_dir = Path(data_dir) / 'teams' / team
            output_path = team_dir / 'season_events.csv'
            team_events.to_csv(output_path, index=False)
            print(f"✓ ({len(team_events)} events)")
        else:
            print("✗ (no events)")

    print(f"\nPreprocessing complete. Saved season_events.csv for each team.")
