"""
Match pipeline and CLI for running metrics.

Orchestrates metric computation for matches and teams,
with command-line interface for easy execution.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import click

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.statsbomb_loader import (
    load_match_events, load_team_season, load_full_league, get_all_teams
)
from metrics.in_possession.style_of_play import StyleOfPlay
from metrics.in_possession.buildup_tactical import BuildupTactical
from metrics.out_of_possession.style_of_defense import StyleOfDefense


def run_single_match(filepath: str) -> dict:
    """
    Load one match file and run all metric modules.

    Args:
        filepath: Path to match JSON file

    Returns:
        Flat dict of all metrics, including match_id and team info.

    Handles exceptions per module gracefully — missing metrics
    don't crash the pipeline.
    """
    try:
        events_df = load_match_events(filepath)

        if len(events_df) == 0:
            return {'error': 'No events loaded'}

        # Get teams
        teams = events_df['team'].dropna().unique()

        result = {
            'source_file': Path(filepath).name,
            'match_id': events_df['match_id'].iloc[0] if len(events_df) > 0 else None,
        }

        # Run metrics for each team
        for team in teams:
            try:
                # Style of Play
                sop = StyleOfPlay(events_df, team)
                result.update(sop.compute())
            except Exception as e:
                print(f"Warning: StyleOfPlay failed for {team}: {e}")

            try:
                # Buildup Tactical
                bt = BuildupTactical(events_df, team)
                result.update(bt.compute())
            except Exception as e:
                print(f"Warning: BuildupTactical failed for {team}: {e}")

            try:
                # Style of Defense
                sd = StyleOfDefense(events_df, team)
                result.update(sd.compute())
            except Exception as e:
                print(f"Warning: StyleOfDefense failed for {team}: {e}")

        return result

    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {'error': str(e)}


def run_team_season(team: str, data_dir: str = "data") -> pd.DataFrame:
    """
    Load all matches for a team and run all metrics per match.

    Args:
        team: Team name
        data_dir: Base data directory

    Returns:
        DataFrame with one row per match, columns = match metadata + all metrics.

    Logs warnings for individual module failures but continues.
    """
    print(f"Loading {team} season...")

    team_events = load_team_season(team, data_dir)

    if len(team_events) == 0:
        print(f"No events loaded for {team}")
        return pd.DataFrame()

    # Get unique match_ids
    match_ids = team_events['match_id'].unique()
    print(f"Found {len(match_ids)} matches for {team}")

    results = []

    for match_id in match_ids:
        match_events = team_events[team_events['match_id'] == match_id].copy()

        result = {
            'team': team,
            'match_id': match_id,
            'n_events': len(match_events),
        }

        try:
            sop = StyleOfPlay(match_events, team)
            result.update(sop.compute())
        except Exception as e:
            print(f"  Warning: StyleOfPlay failed for match {match_id}: {e}")

        try:
            bt = BuildupTactical(match_events, team)
            result.update(bt.compute())
        except Exception as e:
            print(f"  Warning: BuildupTactical failed for match {match_id}: {e}")

        try:
            sd = StyleOfDefense(match_events, team)
            result.update(sd.compute())
        except Exception as e:
            print(f"  Warning: StyleOfDefense failed for match {match_id}: {e}")

        results.append(result)

    return pd.DataFrame(results)


def run_full_league(data_dir: str = "data", teams: list = None) -> pd.DataFrame:
    """
    Run all metrics for all teams (or subset).

    Args:
        data_dir: Base data directory
        teams: List of team names. If None, runs all teams.

    Returns:
        DataFrame with all teams' match-level metrics.
        Saves to data/outputs/league_metrics_{timestamp}.csv
    """
    if teams is None:
        teams = get_all_teams(data_dir)

    print(f"Running full league analysis for {len(teams)} teams...")

    all_results = []

    for team in teams:
        team_df = run_team_season(team, data_dir)
        if len(team_df) > 0:
            all_results.append(team_df)

    if all_results:
        league_df = pd.concat(all_results, ignore_index=True)

        # Save to outputs
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = Path(data_dir) / 'outputs' / f'league_metrics_{timestamp}.csv'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        league_df.to_csv(output_path, index=False)

        print(f"\nSaved league metrics to: {output_path}")
        return league_df
    else:
        return pd.DataFrame()


# ============================================================================
# CLI Interface
# ============================================================================

@click.group()
def cli():
    """Football analytics pipeline CLI."""
    pass


@cli.command()
@click.option('--match', type=click.Path(exists=True),
              help='Path to match JSON file')
def single_match(match):
    """Run metrics on a single match."""
    if not match:
        click.echo("Error: --match required")
        sys.exit(1)

    result = run_single_match(match)
    print("\nMatch metrics:")
    for key, val in sorted(result.items()):
        print(f"  {key}: {val}")


@cli.command()
@click.option('--team', type=str, required=True,
              help='Team name')
@click.option('--data-dir', type=click.Path(exists=True), default='data',
              help='Base data directory')
def team_season(team, data_dir):
    """Run metrics for a full team season."""
    df = run_team_season(team, data_dir)

    print(f"\n{team} season metrics ({len(df)} matches):")
    print(df.head().to_string())
    print(f"\nColumns: {list(df.columns)}")


@cli.command()
@click.option('--data-dir', type=click.Path(exists=True), default='data',
              help='Base data directory')
@click.option('--teams', multiple=True, default=None,
              help='Specific teams (if not provided, runs all)')
def full_league(data_dir, teams):
    """Run metrics for full league."""
    teams_list = list(teams) if teams else None
    df = run_full_league(data_dir, teams_list)

    print(f"\nLeague metrics ({len(df)} matches):")
    print(df.head().to_string())


if __name__ == '__main__':
    cli()
