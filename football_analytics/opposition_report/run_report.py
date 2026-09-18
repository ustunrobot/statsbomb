#!/usr/bin/env python3
"""Report orchestrator: Combines all sections into a single HTML document."""

import sys
import argparse
from pathlib import Path

# Ensure unbuffered output for progress tracking
sys.stdout.flush()
sys.stderr.flush()

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.opposition_report import section0, section1, section2, section3, section4, section5, section6, section7, section8, section9, section10, section11, section12, section13, section14, section15, section16, section21, section_appendix, section1_landscape
from football_analytics.event_based.data_provider import DataProvider
from football_analytics.event_based.event_processor import EventProcessor

def get_team_stats(competition_id: int, season_id: int) -> dict:
    """Process event data and return aggregates for the given team."""
    provider = DataProvider()
    return provider.get_team_stats(competition_id, season_id)

def get_aggregates_for_team(season: str) -> dict:
    """Process event data and return aggregates for the given team."""
    provider = DataProvider()
    processor = EventProcessor()

    # Load and process matches
    matches = provider.get_matches(seasons=[season])  # Specify the season(s) you want to include
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

    # Aggregate stats per team across all matches
    print(f"[PROGRESS]2|95|Aggregating match statistics...", flush=True)
    aggregates_by_layer = processor.aggregate_results(results_by_match)

    return aggregates_by_layer


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
{section21_styles}
{appendix_styles}

</style>"""
    return styles


def render_complete_report(all_metrics, team_metrics, statsbomb_team_metrics, team_name: str, all_player_stats: list = None, league_table: dict = None, report_type: str = "team") -> str:
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
                {appendix_html}
                """
    if report_type == "player":
        player_sections = []
        if all_player_stats:
            for player_stats in all_player_stats:
                player_name_item = player_stats.get('player_name', 'Unknown Player')
                sample_size_item = player_stats.get('sample_size')
                player_position_item = player_stats.get('player_position')
                minutes_threshold = player_stats.get('minutes_threshold')
                section1_html = section1_landscape.render_report_title_section_landscape(team_metrics, report_type, player_name_item, sample_size_item, player_position_item, minutes_threshold)
                section21_html = section21.render_player_radar_section(player_stats)
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

    args = parser.parse_args()

    team_name = args.team
    season = args.season
    league = args.league
    competition_id = args.competition_id
    season_id = args.season_id
    report_type = args.report_type
    player_id = args.player_id

    if player_id:
        print(f"Generating {report_type} opposition report for {team_name} in {season_id}: {season} ({competition_id}: {league}), Player ID: {player_id}...")
    else:
        print(f"Generating {report_type} opposition report for {team_name} in {season_id}: {season} ({competition_id}: {league})...")

    # Initialize data provider
    provider = DataProvider()
    print(f"[PROGRESS]1|10|Loading league table...", flush=True)

    # Get and display league table
    league_table = provider.get_table(int(competition_id), int(season_id))

    # if league_table:
    #     print("\n" + "="*90)
    #     print(f"LEAGUE TABLE - {league}")
    #     print("="*90)
    #     print(f"{'Rank':<6} {'Team':<25} {'P':<3} {'W':<3} {'D':<3} {'L':<3} {'GF':<3} {'GA':<3} {'GD':<4} {'Pts':<3}")
    #     print("-"*90)
    #     for tname, stats in sorted(league_table.items(), key=lambda x: x[1]['rank']):
    #         rank = stats['rank']
    #         played = stats['played']
    #         wins = stats['wins']
    #         draws = stats['draws']
    #         losses = stats['losses']
    #         gf = stats['goals_for']
    #         ga = stats['goals_against']
    #         gd = stats['goal_difference']
    #         pts = stats['points']

    #         # Highlight the team we're generating report for
    #         marker = " ◄" if tname == team_name else ""
    #         print(f"{rank:<6} {tname:<25} {played:<3} {wins:<3} {draws:<3} {losses:<3} {gf:<3} {ga:<3} {gd:<4} {pts:<3}{marker}")
    #     print("="*90 + "\n")

    # Get aggregates from event data
    print(f"[PROGRESS]2|20|Loading match data...", flush=True)
    all_metrics = get_aggregates_for_team(season)
    # Get stats for all teams (organized by team_name)
    print(f"[PROGRESS]3|96|Loading team statistics...", flush=True)
    statsbomb_team_metrics = get_team_stats(competition_id, season_id)
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
    player_name = None
    if report_type == "player":
        # Get player stats for the selected team
        all_team_player_stats = statsbomb_team_metrics

        if player_id:
            # Get stats for specific player
            print(f"[PROGRESS]5|98|Retrieving stats for player ID: {player_id}...", flush=True)
            player_stats = provider.get_player_stats(int(competition_id), int(season_id), player_id)
            if player_stats:
                player_stats_list.append(player_stats)
                player_name = player_stats.get('player_name')
        else:
            # Get stats for all players of the team
            team_player_ids = provider.get_team_players(int(competition_id), int(season_id), team_name)

            if team_player_ids:
                print(f"[PROGRESS]5|98|Retrieving stats for {len(team_player_ids)} players from {team_name}...", flush=True)

                for idx, player_id_item in enumerate(team_player_ids, 1):
                    player_stats = provider.get_player_stats(int(competition_id), int(season_id), player_id_item)
                    if player_stats:
                        player_stats_list.append(player_stats)
                    print(f"[PROGRESS]5|98|Retrieved stats for {idx}/{len(team_player_ids)} players...", flush=True)

    html_output = render_complete_report(all_teams, team_metrics, statsbomb_team_metrics, team_name, player_stats_list, league_table, report_type)

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
