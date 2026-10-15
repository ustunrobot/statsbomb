#!/usr/bin/env python3
"""Report orchestrator: Combines all sections into a single HTML document."""

import sys
import argparse
from pathlib import Path

# Ensure unbuffered output for progress tracking
sys.stdout.flush()
sys.stderr.flush()

sys.path.insert(0, str(Path(__file__).parent.parent))

from opposition_report import section0, section1, section2, section3, section4, section5, section6, section7, section8, section9, section10, section11, section12, section13, section14, section15, section16, section17, section21, section_appendix, section1_landscape
from event_based.data_provider import DataProvider
from event_based.event_processor import EventProcessor
from event_based.metrics import Metric

def get_team_stats(competition_id: int, season_id: int, data_root: str = None, team_name: str = None, week_no: int = None) -> dict:
    """Process event data and return aggregates for the given team."""
    provider = DataProvider(data_root=data_root)
    return provider.get_team_stats(competition_id, season_id, team_name=team_name, week_no=week_no)

def get_week_match_teams(provider: DataProvider, team_name: str, season_name: str, week_no: int):
    """
    Resolve the home/away team names (StatsBomb convention) for team_name's
    week_no match, from its event filename (see DataProvider.get_team_weeks).

    Returns (home_name, away_name), or (None, None) if team_name, week_no or
    season_name is missing, or no match is found for that week.
    """
    if not (team_name and week_no is not None and season_name):
        return None, None

    weeks = provider.get_team_weeks(team_name, season_name)
    week_entry = next((w for w in weeks if w['week_no'] == week_no), None)
    if week_entry is None:
        return None, None

    return provider._get_teams_from_filename(week_entry['filename'])

def get_team_stats_sk(competition_id: int, season_id: int, data_root: str = None, team_name: str = None,
                       week_no: int = None, season_name: str = None) -> dict:
    """Process event data and return aggregates for the given team.

    When team_name, week_no and season_name are all given, team_name's season-level
    SkillCorner stats are overridden with its match-level stats for that week.
    """
    provider = DataProvider(data_root=data_root)

    home_name, away_name = get_week_match_teams(provider, team_name, season_name, week_no)
    if home_name and away_name:
        return provider.get_team_stats_sk(
            competition_id, season_id, team_name=team_name, home_name=home_name, away_name=away_name
        )

    return provider.get_team_stats_sk(competition_id, season_id)

def _find_team_aggregate(team_aggregates: dict, team_name: str) -> dict:
    """Find a layer's aggregate dict for team_name among its team_id-keyed entries."""
    return next(
        (team_data for team_data in team_aggregates.values()
         if isinstance(team_data, dict) and team_data.get('team_name') == team_name),
        None
    )

def get_aggregates_for_team(season: str, data_root: str = None, team_name: str = None, week_no: int = None) -> dict:
    """Process event data and return aggregates for the given team.

    When both team_name and week_no are given, every KPI-layer metric for
    team_name is computed from just that week's match (other teams' matches
    are unaffected), and each such metric's original full-season z-score is
    preserved on its secondary_z_score field - mirroring get_team_stats()'s
    week-override behavior. Every match is loaded and run through
    process_event_file() exactly once; the week filtering and the extra
    aggregation pass needed to capture the original z-scores are both applied
    afterward, directly on the in-memory per-match results, so no event file
    is re-processed.
    """
    provider = DataProvider(data_root=data_root)
    processor = EventProcessor()

    # Load every match for the season, unfiltered - team_name/week_no filtering
    # (if any) is applied below, directly on the already-processed results.
    matches = provider.get_matches(seasons=[season])
    total_matches = len(matches)
    print(f"Processing {total_matches} matches...", flush=True)
    print(f"[PROGRESS]2|60|Processing event data: Loading files...", flush=True)

    results_by_match = []
    for idx, (filename, events_dict) in enumerate(matches, 1):
        # Extract readable match info from filename (convert Path to string if needed)
        filename_str = str(filename)
        match_info = filename_str.split('/')[-1] if '/' in filename_str else filename_str

        results = processor.process_event_file(events_dict)
        results_by_match.append((filename, results))

        # Calculate progress: 60% to 95% range for processing matches
        progress_percent = 60 + int((idx / total_matches) * 34)
        print(f"[PROGRESS]2|{progress_percent}|Processing event data: {idx}/{total_matches} - {match_info}...", flush=True)

    print(f"[PROGRESS]2|95|Aggregating match statistics...", flush=True)

    if team_name and week_no is not None:
        # Full-season aggregate (every match, including team_name's other weeks) -
        # used only to capture team_name's original z-scores before restricting
        # its matches to week_no below.
        original_aggregates_by_layer = processor.aggregate_results(results_by_match)
        original_z_scores_by_layer = {}
        for layer_name, team_aggregates in original_aggregates_by_layer.items():
            team_data = _find_team_aggregate(team_aggregates, team_name)
            if team_data:
                original_z_scores_by_layer[layer_name] = {
                    metric_key: metric.z_score for metric_key, metric in team_data.items()
                    if isinstance(metric, Metric)
                }

        # Same filter DataProvider.get_matches() applies when team_name/week_no are
        # both given: drop team_name's matches in every other week, leave every
        # other team's matches untouched - applied here on the in-memory results
        # instead of re-reading match files from disk.
        results_by_match = [
            (filename, results) for filename, results in results_by_match
            if team_name not in provider._get_teams_from_filename(filename.name)
            or provider._get_week_from_filename(filename.name) == week_no
        ]

        aggregates_by_layer = processor.aggregate_results(results_by_match)

        for layer_name, original_z_scores in original_z_scores_by_layer.items():
            team_data = _find_team_aggregate(aggregates_by_layer.get(layer_name, {}), team_name)
            if team_data:
                for metric_key, metric in team_data.items():
                    if isinstance(metric, Metric) and metric_key in original_z_scores:
                        metric.secondary_z_score = original_z_scores[metric_key]

        return aggregates_by_layer

    # No week override requested - aggregate stats per team across all matches
    return processor.aggregate_results(results_by_match)


def get_all_styles() -> str:
    """Collect all styles from all sections."""
    styles = section1.get_styles()
    # Remove the <style> opening tag from other sections, then merge
    section1_landscape_styles = section1_landscape.get_styles().replace("<style>", "").replace("</style>", "")
    section0_styles = section0.get_styles().replace("<style>", "").replace("</style>", "")
    section2_styles = section2.get_styles().replace("<style>", "").replace("</style>", "")
    section3_styles = section3.get_styles().replace("<style>", "").replace("</style>", "")
    section4_styles = section4.get_styles().replace("<style>", "").replace("</style>", "")
    section5_styles = section5.get_styles().replace("<style>", "").replace("</style>", "")
    section6_styles = section6.get_styles().replace("<style>", "").replace("</style>", "")
    section7_styles = section7.get_styles().replace("<style>", "").replace("</style>", "")
    section8_styles = section8.get_styles().replace("<style>", "").replace("</style>", "")
    section9_styles = section9.get_styles().replace("<style>", "").replace("</style>", "")
    section10_styles = section10.get_styles().replace("<style>", "").replace("</style>", "")
    section11_styles = section11.get_styles().replace("<style>", "").replace("</style>", "")
    section12_styles = section12.get_styles().replace("<style>", "").replace("</style>", "")
    section13_styles = section13.get_styles().replace("<style>", "").replace("</style>", "")
    section14_styles = section14.get_styles().replace("<style>", "").replace("</style>", "")
    section15_styles = section15.get_styles().replace("<style>", "").replace("</style>", "")
    section16_styles = section16.get_styles().replace("<style>", "").replace("</style>", "")
    section17_styles = section17.get_styles().replace("<style>", "").replace("</style>", "")
    section21_styles = section21.get_styles().replace("<style>", "").replace("</style>", "")
    appendix_styles = section_appendix.get_styles().replace("<style>", "").replace("</style>", "")

    # Extract content between <style> tags from section1 and add all other sections
    if "<style>" in styles and "</style>" in styles:
        content = styles.split("<style>")[1].split("</style>")[0]
        return f"""<style>

{content}
{section1_landscape_styles}
{section0_styles}
{section2_styles}
{section3_styles}
{section4_styles}
{section5_styles}
{section6_styles}
{section7_styles}
{section8_styles}
{section9_styles}
{section10_styles}
{section11_styles}
{section12_styles}
{section13_styles}
{section14_styles}
{section15_styles}
{section16_styles}
{section17_styles}
{section21_styles}
{appendix_styles}

</style>"""
    return styles


def render_complete_report(all_metrics, team_metrics, statsbomb_team_metrics, skillcorner_team_metrics, team_name: str, all_player_stats: list = None, all_player_stats_sk: list = None, league_table: dict = None, report_type: str = "team") -> str:
    """Render complete report combining all sections."""
    # Render each section
    if report_type == "team":
        section0_html = section0.render_derived_metrics_section(team_metrics)
        section1_html = section1.render_report_title_section(team_metrics, report_type)
        section3_html = section3.render_radar_section(all_metrics, team_metrics, statsbomb_team_metrics, team_name, league_table)
        section4_html = section4.render_shot_type_section(team_metrics)
        section8_html = section8.render_derived_metrics_section(team_metrics)
        section9_html = section9.render_derived_metrics_section(team_metrics, statsbomb_team_metrics, team_name)
        section10_html = section10.render_radar_section(all_metrics, team_metrics, statsbomb_team_metrics, team_name, league_table)
        section11_html = section11.render_aerial_thirds_section(team_metrics, statsbomb_team_metrics, team_name)
        section12_html = section12.render_median_positions_section(team_metrics, team_name, all_player_stats)
        section13_html = section13.render_defending_section(team_metrics, statsbomb_team_metrics)
        section14_html = section14.render_radar_section(all_metrics, team_metrics, statsbomb_team_metrics, team_name, league_table)
        section15_html = section15.render_pressure_heatmap_section(team_metrics, team_name)
        section16_html = section16.render_performance_trends_section(team_metrics, team_name)
        section17_html = section17.render_physical_data_section(skillcorner_team_metrics, team_name)
        appendix_html = section_appendix.render_appendix_section()
        #section6_html = section6.render_pressing_heatmap_section(section6.section_data)
        #section7_html = section7.render_passing_section(all_metrics)


        # Combine all sections
        sections = f"""
                {section1_html}
                {section0_html}
                {section3_html}
                {section4_html}
                {section8_html}
                {section9_html}
                {section10_html}
                {section11_html}
                {section12_html}
                {section13_html}
                {section14_html}
                {section15_html}
                {section16_html}
                {section17_html}
                {appendix_html}
                """
    if report_type == "player":
        player_sections = []

        # Build a lookup of SkillCorner physical stats by StatsBomb player_id, since
        # all_player_stats and all_player_stats_sk are independently filtered lists
        # and may not be aligned index-for-index.
        sk_stats_by_player_id = {}
        if all_player_stats_sk:
            for stats_sk in all_player_stats_sk:
                pid = None
                for source_key in ('player_all', 'player_h1', 'player_h2', 'player_otip', 'player_tip'):
                    source = stats_sk.get(source_key)
                    if source and source.get('player_id') is not None:
                        pid = source.get('player_id')
                        break
                if pid is not None:
                    sk_stats_by_player_id[pid] = stats_sk

        if all_player_stats:
            for player_stats in all_player_stats:
                player_name_item = player_stats.get('player_name', 'Unknown Player')
                sample_size_item = player_stats.get('sample_size')
                player_position_item = player_stats.get('player_position')
                minutes_threshold = player_stats.get('minutes_threshold')
                player_stats_sk = sk_stats_by_player_id.get(player_stats.get('player_id'), {})
                section1_html = section1_landscape.render_report_title_section_landscape(team_metrics, report_type, player_name_item, sample_size_item, player_position_item, minutes_threshold)
                section21_html = section21.render_player_radar_section(player_stats, player_stats_sk)
                player_sections.append(section1_html)
                player_sections.append(section21_html)

        sections = f"""
                        {''.join(player_sections)}
                    """

    # Build complete HTML document
    container_class = "a4-container-landscape" if report_type == "player" else "a4-container"
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Opponent Intelligence Report</title>
        {get_all_styles()}
    </head>
    <body>
        <div class="{container_class}">
            {sections}
        </div>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate opposition report for a team')
    parser.add_argument('team', help='Team name to generate report for')
    parser.add_argument('season', help='Season name (e.g., "2025/2026")')
    parser.add_argument('league', help='League name (e.g., "EFL League Two")')
    parser.add_argument('competition_id', help='Competition ID (e.g., "12345")')
    parser.add_argument('season_id', help='Season ID (e.g., "12345")')
    parser.add_argument('report_type', choices=['player', 'team'], help='Report type: "player" or "team"')
    parser.add_argument('--player-id', type=int, default=None, help='Optional: Player ID to include in report')
    parser.add_argument('--data-root', default=None, help='Directory containing downloaded team match-event folders (defaults to a path relative to this file, for local/dev runs)')
    parser.add_argument('--week-no', type=int, default=None, help="Optional: Restrict team's matches to this week number only (other teams' matches are unaffected)")

    args = parser.parse_args()

    team_name = args.team
    season = args.season
    league = args.league
    competition_id = args.competition_id
    season_id = args.season_id
    report_type = args.report_type
    player_id = args.player_id
    data_root = args.data_root
    week_no = args.week_no

    if player_id:
        print(f"Generating {report_type} opposition report for {team_name} in {season_id}: {season} ({competition_id}: {league}), Player ID: {player_id}...")
    else:
        print(f"Generating {report_type} opposition report for {team_name} in {season_id}: {season} ({competition_id}: {league})...")

    # Initialize data provider
    provider = DataProvider(data_root=data_root)
    print(f"[PROGRESS]1|10|Loading league table...", flush=True)

    # Get and display league table
    league_table = provider.get_table(int(competition_id), int(season_id))

    # Get aggregates from event data
    print(f"[PROGRESS]2|20|Loading match data...", flush=True)
    all_metrics = get_aggregates_for_team(season, data_root=data_root, team_name=team_name, week_no=week_no)
    # Get stats for all teams (organized by team_name)
    print(f"[PROGRESS]3|96|Loading team statistics...", flush=True)
    statsbomb_team_metrics = get_team_stats(competition_id, season_id, data_root=data_root, team_name=team_name, week_no=week_no)
    skillcorner_team_metrics = get_team_stats_sk(
        competition_id, season_id, data_root=data_root, team_name=team_name, week_no=week_no, season_name=season
    )

    # Resolve the week's home/away team names once, for overriding player SkillCorner
    # stats with their match-level numbers (see get_player_stats_sk calls below).
    player_sk_home_name, player_sk_away_name = get_week_match_teams(provider, team_name, season, week_no)

    # Get stats for all players
    #all_player_stats = provider.get_all_player_stats(competition_id, season_id)
    #print(f"✓ Loaded team metrics from StatsBomb data provider.")
    #print(statsbomb_team_metrics)
    
    print(f"[PROGRESS]4|97|Building team metrics...", flush=True)
    #print(f"✓ Loaded player metrics from StatsBomb data provider.")
    #print(statsbomb_player_metrics.get('player_season_minutes'))

    # Find team metrics by looping through and matching team_name field
    # Collect metrics from ALL layers
    team_metrics = {}
    for layer_name, layer_data in all_metrics.items():
        if isinstance(layer_data, dict):
            for team_id, team_data in layer_data.items():
                if isinstance(team_data, dict) and team_data.get('team_name') == team_name:
                    # Merge metrics from this layer into team_metrics
                    team_metrics.update(team_data)
    team_metrics['season'] = season  # Ensure season is included
    team_metrics['league'] = league  # Include league information

    # Combine metrics from all layers into a single structure organized by team_id
    all_teams = {}
    for layer_name, layer_data in all_metrics.items():
        if isinstance(layer_data, dict):
            for team_id, team_data in layer_data.items():
                if team_id not in all_teams:
                    all_teams[team_id] = {}
                # Merge metrics from this layer into the team entry
                all_teams[team_id].update(team_data)

    team_metrics['total_teams'] = len(all_teams)
    # Render the complete report with metrics
    print(f"[PROGRESS]5|98|Rendering report sections...", flush=True)

    player_stats_list = []
    player_stats_list_sk = []
    #player_name = None
    if report_type == "player":
        # Get player stats for the selected team        

        if player_id:
            # Get stats for specific player
            print(f"[PROGRESS]5|98|Retrieving stats for player ID: {player_id}...", flush=True)
            player_stats = provider.get_player_stats(
                int(competition_id), int(season_id), player_id, team_name=team_name, week_no=week_no
            )
            if player_stats:
                player_stats_list.append(player_stats)
                #player_name = player_stats.get('player_name')
            player_stats_sk = provider.get_player_stats_sk(
                int(competition_id), int(season_id), player_id,
                team_name=team_name, home_name=player_sk_home_name, away_name=player_sk_away_name
            )
            if player_stats_sk:
                player_stats_list_sk.append(player_stats_sk)
        else:
            # Get stats for all players of the team
            team_player_ids = provider.get_team_players(int(competition_id), int(season_id), team_name)

            if team_player_ids:
                print(f"[PROGRESS]5|98|Retrieving stats for {len(team_player_ids)} players from {team_name}...", flush=True)

                for idx, player_id_item in enumerate(team_player_ids, 1):
                    player_stats = provider.get_player_stats(
                        int(competition_id), int(season_id), player_id_item, team_name=team_name, week_no=week_no
                    )
                    if player_stats:
                        player_stats_list.append(player_stats)

                    player_stats_sk = provider.get_player_stats_sk(
                        int(competition_id), int(season_id), player_id_item,
                        team_name=team_name, home_name=player_sk_home_name, away_name=player_sk_away_name
                    )
                    if player_stats_sk:
                        player_stats_list_sk.append(player_stats_sk)

                    print(f"[PROGRESS]5|98|Retrieved stats for {idx}/{len(team_player_ids)} players...", flush=True)

    html_output = render_complete_report(all_teams, team_metrics, statsbomb_team_metrics, skillcorner_team_metrics, team_name, player_stats_list, player_stats_list_sk, league_table, report_type)

    # Save HTML output to file
    print(f"[PROGRESS]6|99|Saving report...", flush=True)
    report_path = Path(__file__).parent / 'report.html'
    with open(report_path, 'w') as f:
        f.write(html_output)
    print(f"[PROGRESS]7|100|Report saved to {report_path}", flush=True)
    print(f"✓ Report saved to {report_path}", flush=True)


    # Output HTML to stdout for direct frontend display
    # Use a marker to separate from other output
    print("\n<<<HTML_START>>>", flush=True)
    print(html_output, flush=True)
    print("<<<HTML_END>>>", flush=True)
    sys.stdout.flush()
