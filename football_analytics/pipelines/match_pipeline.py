"""
Match pipeline and CLI for running metrics.

Orchestrates metric computation for matches and teams,
with command-line interface for easy execution.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import List, Dict
import click

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.statsbomb_loader import (
    load_match_events, load_team_season, load_full_league, get_all_teams
)
from utils.buildup import find_buildups, summarize_buildups
from utils.shape import find_shape, visualize_shape
from metrics.in_possession.style_of_play import StyleOfPlay
from metrics.in_possession.buildup_tactical import BuildupTactical
from metrics.out_of_possession.style_of_defense import StyleOfDefense
from metrics.match_wise.match_info import MatchInfo
from utils.types import TeamStats
from utils.buildup import export_buildups_to_csv
from utils.report import generate_team_report



def run_team_season(team: str, data_dir: str = "data", use_combined: bool = False, update_combined: bool = False, week: int = None) -> TeamStats:
    """
    Load all matches for a team and run all metrics per match.

    Args:
        team: Team name
        data_dir: Base data directory
        use_combined: If True, load from preprocessed season_events.csv (faster).
                     If False, load from individual match JSON files.
        week: Optional week number to filter (e.g., 15 for Week15_*.json).

    Returns:
        TeamStats object containing the computed metrics and buildups.

    Logs warnings for individual module failures but continues.
    """
    print(f"Loading {team} season...", end=" ")
    timenow = datetime.now()

    if use_combined:
        # Load from preprocessed CSV
        combined_path = Path(data_dir) / 'teams' / team / 'season_events.csv'
        if combined_path.exists():
            print("(from combined CSV)")
            team_events = pd.read_csv(combined_path)
        else:
            print("(combined CSV not found, falling back to JSON files)")
            team_events = load_team_season(team, data_dir, week=week)
    else:
        print("(from JSON files)")
        team_events = load_team_season(team, data_dir, week=week)

    if len(team_events) == 0:
        print(f"No events loaded for {team}")
        return pd.DataFrame()

    print(f"Loaded {len(team_events)} events for {team} in {int((datetime.now() - timenow).total_seconds())} seconds")

    if update_combined:
        combined_path = Path(data_dir) / 'teams' / team / 'season_events.csv'
        combined_path.parent.mkdir(parents=True, exist_ok=True)
        team_events.to_csv(combined_path, index=False)
        print(f"  Saved combined events to: {combined_path}")

    result = TeamStats(
        team=team,
        n_events=len(team_events),
        n_matches=team_events['match_id'].nunique(),
        n_metrics=76,
    )

    timenow = datetime.now()
    try:        
        sop = StyleOfPlay(team_events, team)
        result.style_of_play = sop.compute()        
        print(f"  Computed Style of Play for team {team} in {int((datetime.now() - timenow).total_seconds())} seconds")
    except Exception as e:
        print(f"  Warning: StyleOfPlay failed for team {team}: {e}")

    timenow = datetime.now()
    try:
        buildups = find_buildups(team_events, team=team)
        print(f"  Extracted {len(buildups)} buildups for team {team} in {int((datetime.now() - timenow).total_seconds())} seconds")        
        if buildups:
            timenow = datetime.now()
            result.buildup_stats = summarize_buildups(buildups)
            result.buildups = buildups
            print(f"  Summarized buildups for team {team} in {int((datetime.now() - timenow).total_seconds())} seconds")
        else:
            result.buildup_stats = {}
            result.buildups = []
    except Exception as e:
            print(f"  Warning: Buildup extraction failed for team {team}: {e}")

    try:
        result.shape = find_shape(result.buildups)

        if "medians" in result.shape:
            # Visualize median Ball Receipt locations for all positions
            visualize_shape(result.shape["medians"], title="Median Ball Receipt - All Positions")

        
        generate_team_report(team, result)            

    except Exception as e:
        print(f"  Warning: Shape failed for team {team}: {e}")

    try:
        pass
        #bt = BuildupTactical(team_events, team)
        #result.update(bt.compute())
    except Exception as e:
        print(f"  Warning: BuildupTactical failed for team {team}: {e}")

    try:
        pass
        #sd = StyleOfDefense(team_events, team)
        #result.update(sd.compute())
    except Exception as e:
        print(f"  Warning: StyleOfDefense failed for team {team}: {e}")    


    return result


def run_full_league(data_dir: str = "data", teams: list = None, use_combined: bool = False, week: int = None, save: bool = False, update_combined: bool = False, visualize: bool = False):
    """
    Run all metrics for all teams (or subset), aggregated per team.

    Args:
        data_dir: Base data directory
        teams: List of team names. If None, runs all teams.
        use_combined: If True, load from preprocessed season_events.csv (faster).
        week: Optional week number to filter (e.g., 15 for Week15_*.json).
        save: If True, save results to CSV file.
        visualize: If True, visualize median event locations for all positions.

    Returns:
        DataFrame with one row per team, columns = team name + averaged metrics.
        Saves to data/outputs/league_metrics_{timestamp}.csv only if save=True
    """
    if teams is None:
        teams = get_all_teams(data_dir)

    print(f"Running full league analysis for {len(teams)} teams...")

    all_results = []

    for team in teams:
        team_result = run_team_season(team, data_dir, use_combined=use_combined, update_combined=update_combined, week=week)
        if team_result:
            all_results.append(team_result)
            
    if all_results:
        # Debug: print style_of_play for each result
        league_df = []
        for result in all_results:
            print(f"Team: {result.team}, Events: {result.n_events}")
            print("  Style of Play:")
            for key, value in result.style_of_play.items():
                print(f"    {key}: {value}")
            print("  Buildup Stats:")
            for key, value in result.buildup_stats.items():
                print(f"    {key}: {value}")

            merged_stats = {
                'team': result.team,
                'n_events': result.n_events,
            }
            merged_stats.update(result.style_of_play)
            merged_stats.update(result.buildup_stats)
            df = pd.DataFrame([merged_stats])
            league_df.append(df)
            export_buildups_to_csv(result.buildups, f"data/outputs/buildups_{result.team}.csv")

        # # Aggregate by team: average style_of_play and buildup_stats metrics
        # numeric_cols = league_df.select_dtypes(include=['number']).columns
        # agg_dict = {col: 'mean' for col in numeric_cols}

        team_agg = pd.concat(league_df, ignore_index=True)

        if save:
            # Save aggregated team metrics to CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = Path(data_dir) / 'outputs' / f'league_metrics_{timestamp}.csv'
            output_path.parent.mkdir(parents=True, exist_ok=True)
            team_agg.to_csv(output_path, index=False)
            print(f"\nSaved league metrics to: {output_path}")
        # print(f"Columns: {list(team_agg.columns)}")





# ============================================================================
# CLI Interface
# ============================================================================

def run_pipeline(teams: list = None, data_dir: str = "data", use_combined: bool = False, week: int = None, save: bool = False, update_combined: bool = False, visualize: bool = False) -> None:
    """
    Unified pipeline that processes matches and teams.

    Args:
        teams: List of team names. If None, processes all teams.
        data_dir: Base data directory.
        use_combined: If True, load from preprocessed season_events.csv (faster).
        week: Optional week number to filter (e.g., 15 for Week15_*.json).
        save: If True, save results to CSV file.
        visualize: If True, visualize median event locations for all positions.
    """
    if teams:
        # Selected teams mode
        teams_list = list(teams)
        print(f"\nProcessing {len(teams_list)} selected team(s)...")
        df = run_full_league(data_dir, teams_list, use_combined=use_combined, week=week, save=save, update_combined=update_combined, visualize=visualize)
        print(f"\nProcessed metrics for teams: {', '.join(teams_list)}")
    else:
        # Full league mode (all teams)
        print("\nProcessing all teams in league...")
        df = run_full_league(data_dir, None, use_combined=use_combined, week=week, save=save, update_combined=update_combined, visualize=visualize)
        print("\nFull league analysis complete")


@click.command()
@click.option('--teams', multiple=True, default=None,
              help='Specific teams (if not provided, runs all teams)')
@click.option('--week', type=int, default=None,
              help='Week number to filter (e.g., 15 for Week15_*.json). Cannot be used with --use-combined')
@click.option('--data-dir', type=click.Path(exists=True), default='data',
              help='Base data directory')
@click.option('--use-combined', is_flag=True,
              help='Load from preprocessed season_events.csv (faster). Cannot be used with --week')
@click.option('--save', is_flag=True,
              help='Save results to CSV file')
@click.option('--update-combined', is_flag=True,
              help='Save combine events to CSV file')
@click.option('--visualize', is_flag=True,
              help='Visualize median event locations for all positions')
def main(teams, week, data_dir, use_combined, save, update_combined, visualize):
    """
    Football analytics pipeline.

    Default: Process all teams and all their matches.
    With --teams: Process only specified teams and their matches.
    With --week: Process only matches from a specific week.
    With --save: Save results to CSV file.
    With --visualize: Generate visualizations.
    """
    if week and use_combined:
        click.echo("Error: --week and --use-combined cannot be used together")
        sys.exit(1)

    run_pipeline(
        teams=list(teams) if teams else None,
        data_dir=data_dir,
        use_combined=use_combined,
        week=week,
        save=save,
        update_combined=update_combined,
        visualize=visualize
    )


if __name__ == '__main__':
    main()
