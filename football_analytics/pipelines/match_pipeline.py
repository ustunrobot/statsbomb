"""
Match pipeline and CLI for running metrics.

Orchestrates metric computation for matches and teams,
with command-line interface for easy execution.
"""

import sys
import json
from pathlib import Path
from dataclasses import asdict
import pandas as pd
from datetime import datetime
from typing import List, Dict
import click


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for non-serializable objects."""
    def default(self, obj):
        if isinstance(obj, (pd.DataFrame, pd.Series)):
            return obj.to_dict()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.statsbomb_loader import (
    load_team_season, get_all_teams
)
from utils.buildup import find_buildups, summarize_buildups
from utils.shape import find_shape, visualize_shape, find_shape_from_ball_receipts, visualize_touch
from metrics.in_possession.style_of_play import StyleOfPlay
from metrics.in_possession.buildup_tactical import BuildupTactical
from metrics.out_of_possession.style_of_defense import StyleOfDefense
from metrics.match_wise.match_info import MatchInfo
from utils.team_types import TeamStats, TeamMetrics
from utils.buildup import export_buildups_to_csv
from reports.team_report.report import generate_team_report



def run_team_season(team: str, data_dir: str = "data", use_combined: bool = False, update_combined: bool = False, season: str = None, week: int = None, report: bool = None) -> TeamStats:
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

    if report:
        generate_team_report(team)            
        return
    print(f"Loading {team} season...", end=" ")
    timenow = datetime.now()

    if use_combined:
        # Load from preprocessed CSV
        combined_path = Path(data_dir) / 'teams' / team / 'all_events.csv'
        if combined_path.exists():
            print("(from combined CSV)")
            team_events = pd.read_csv(combined_path)
        else:
            print("(combined CSV not found, falling back to JSON files)")
            team_events = load_team_season(team, data_dir, season=season, week=week)
    else:
        print("(from JSON files)")
        team_events = load_team_season(team, data_dir, season=season, week=week)

    if len(team_events) == 0:
        print(f"No events loaded for {team}")
        return None

    print(f"Loaded {len(team_events)} events for {team} in {int((datetime.now() - timenow).total_seconds())} seconds")

    if update_combined:
        combined_path = Path(data_dir) / 'teams' / team / 'all_events.csv'
        combined_path.parent.mkdir(parents=True, exist_ok=True)
        team_events.to_csv(combined_path, index=False)
        print(f"  Saved combined events to: {combined_path}")

    metrics = TeamMetrics(        
        n_events=len(team_events),
        n_matches=team_events['match_id'].nunique(),
        n_metrics=76,
    )

    timenow = datetime.now()
    try:        
        sop = StyleOfPlay(team_events, team)
        metrics.style_of_play = sop.compute()        
        print(f"  Computed Style of Play for team {team} in {int((datetime.now() - timenow).total_seconds())} seconds")
    except Exception as e:
        print(f"  Warning: StyleOfPlay failed for team {team}: {e}")

    timenow = datetime.now()
    try:
        buildups = find_buildups(team_events, team=team)
        print(f"  Extracted {len(buildups)} buildups for team {team} in {int((datetime.now() - timenow).total_seconds())} seconds")        
        if buildups:
            timenow = datetime.now()
            metrics.buildup_stats = summarize_buildups(buildups)
            metrics.buildups = buildups
            print(f"  Summarized buildups for team {team} in {int((datetime.now() - timenow).total_seconds())} seconds")
        else:
            metrics.buildup_stats = {}
            metrics.buildups = []
    except Exception as e:
            print(f"  Warning: Buildup extraction failed for team {team}: {e}")

    try:
        metrics.shape = find_shape(metrics.buildups)
        fsback = find_shape_from_ball_receipts(team_events, team, "Back")
        fsmid = find_shape_from_ball_receipts(team_events, team, "Midfield")
        if "medians" in metrics.shape:
            # Visualize median Ball Receipt locations for all positions
            visualize_shape(metrics.shape["medians"], title="MedianPositions")

        if "medians" in fsback:
                # Visualize median Ball Receipt locations for all positions
                visualize_shape(fsback["medians"], title="MedianPositions2")
                visualize_touch(fsback['all_touches'], title="touches-back")
                #print(fs["all_touches"])
        if "medians" in fsmid:
            visualize_touch(fsmid['all_touches'], title="touches-mid")
        
        
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

    result = TeamStats(team=team, all=metrics)
    
    return result


def run_full_league(data_dir: str = "data", teams: list = None, use_combined: bool = False, season: str = None, week: int = None, save: bool = False, update_combined: bool = False, report: bool = False, print_result: bool = False):
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

    all_team_stats = []

    for team in teams:
        team_result = run_team_season(team, data_dir, use_combined=use_combined, update_combined=update_combined, season=season, week=week, report=report)
        if team_result:
            team_result.buildups = None # dont save the buildups
            all_team_stats.append(team_result)
            if print_result:
                light_result = team_result
                light_result.all.buildups = None                
                print(light_result.all)
            
    if all_team_stats and save:
        output_path = Path(data_dir) / "all_teams_stats.json"
        # Convert TeamStats objects to dictionaries
        stats_dicts = [asdict(stat) for stat in all_team_stats]
        with open(output_path, 'w') as f:
            json.dump(stats_dicts, f, indent=2, cls=JSONEncoder)
        print(f"✓ Saved all teams stats to {output_path}")

        





# ============================================================================
# CLI Interface
# ============================================================================

def run_pipeline(teams: list = None, data_dir: str = "data", use_combined: bool = False, season: str = None, week: int = None, save: bool = False, update_combined: bool = False, report: bool = False, print_result: bool = False) -> None:
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
        df = run_full_league(data_dir, teams_list, use_combined=use_combined, season=season, week=week, save=save, update_combined=update_combined, report=report, print_result=print_result)
        print(f"\nProcessed metrics for teams: {', '.join(teams_list)}")
    else:
        # Full league mode (all teams)
        print("\nProcessing all teams in league...")
        df = run_full_league(data_dir, None, use_combined=use_combined, season=season, week=week, save=save, update_combined=update_combined, report=report, print_result=print_result)
        print("\nFull league analysis complete")


@click.command()
@click.option('--teams', multiple=True, default=None,
              help='Specific teams (if not provided, runs all teams)')
@click.option('--week', type=int, default=None,
              help='Week number to filter (e.g., 15 for Week15_*.json). Cannot be used with --use-combined shoul be used with season')
@click.option('--data-dir', type=click.Path(exists=True), default='data',
              help='Base data directory')
@click.option('--use-combined', is_flag=True,
              help='Load from preprocessed season_events.csv (faster). Cannot be used with --week')
@click.option('--save', is_flag=True,
              help='Save results to CSV file')
@click.option('--update-combined', is_flag=True,
              help='Save combine events to CSV file')
@click.option('--report', is_flag=True,
              help='Generate team report')
@click.option('--print-result', is_flag=True,
              help='Generate team report')
@click.option('--season', type=str, default=None,
              help='Season to filter (e.g., 25-26). Cannot be used with --use-combined')

def main(teams, season, week, data_dir, use_combined, save, update_combined, report, print_result):
    """
    Football analytics pipeline.

    Default: Process all teams and all their seasons all matches.
    With --teams: Process only specified teams and their matches.
    With --week: Process only matches from a specific week.
    With --season: Process only matches from a specific season.
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
        season=season,
        week=week,
        save=save,
        update_combined=update_combined,
        report=report,
        print_result=print_result
    )


if __name__ == '__main__':
    main()
