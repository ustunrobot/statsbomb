#!/usr/bin/env python3
"""Report orchestrator: Combines all sections into a single HTML document."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.opposition_report import section0, section1, section2, section3, section4, section5, section6, section7
from football_analytics.event_based.data_provider import DataProvider
from football_analytics.event_based.event_processor import EventProcessor

def get_team_stats(competition_id: int, season_id: int, team_name: str) -> dict:
    """Process event data and return aggregates for the given team."""
    provider = DataProvider()
    return provider.get_team_stats(competition_id, season_id, team_name)


def get_player_stats(competition_id: int, season_id: int, player_id: int) -> dict:
    """Process event data and return player statistics for the given competition and season."""
    provider = DataProvider()
    return provider.get_player_stats(competition_id, season_id, player_id)  # Return stats for all players


def get_aggregates_for_team(season: str) -> dict:
    """Process event data and return aggregates for the given team."""
    provider = DataProvider()
    processor = EventProcessor()

    # Load and process matches
    matches = provider.get_matches(seasons=[season])  # Specify the season(s) you want to include
    print(f"Processing {len(matches)} matches...")

    results_by_match = []
    for filename, events_dict in matches:
        results = processor.process_event_file(events_dict, filename)
        results_by_match.append((filename, results))

    # Aggregate stats per team across all matches
    aggregates_by_layer = processor.aggregate_results(results_by_match)

    return aggregates_by_layer


def get_all_styles() -> str:
    """Collect all styles from all sections."""
    styles = section1.get_styles()
    # Remove the <style> opening tag from other sections, then merge
    section0_styles = section0.get_styles().replace("<style>", "").replace("</style>", "")
    section2_styles = section2.get_styles().replace("<style>", "").replace("</style>", "")
    section3_styles = section3.get_styles().replace("<style>", "").replace("</style>", "")
    section4_styles = section4.get_styles().replace("<style>", "").replace("</style>", "")
    section5_styles = section5.get_styles().replace("<style>", "").replace("</style>", "")
    section6_styles = section6.get_styles().replace("<style>", "").replace("</style>", "")
    section7_styles = section7.get_styles().replace("<style>", "").replace("</style>", "")

    # Extract content between <style> tags from section1 and add all other sections
    if "<style>" in styles and "</style>" in styles:
        content = styles.split("<style>")[1].split("</style>")[0]
        return f"""<style>
{content}
{section0_styles}
{section2_styles}
{section3_styles}
{section4_styles}
{section5_styles}
{section6_styles}
{section7_styles}
</style>"""
    return styles


def render_complete_report(all_metrics, statsbomb_team_metrics) -> str:
    """Render complete report combining all sections."""
    # Render each section
    section0_html = section0.render_derived_metrics_section(all_metrics)
    section1_html = section1.render_report_title_section(all_metrics)
    #section2_html = section2.render_metrics_section(all_metrics)
    section3_html = section3.render_radar_section(all_metrics, statsbomb_team_metrics)
    #section4_html = section4.render_shot_type_section(all_metrics)
    #section5_html = section5.render_defending_section(all_metrics)
    #section6_html = section6.render_pressing_heatmap_section(all_metrics)
    #section7_html = section7.render_passing_section(all_metrics)

    # Combine all sections
    sections = f"""
            {section1_html}
            {section0_html}
            {section3_html}
            {section0_html}
            {section0_html}
            {section0_html}
            {section0_html}
            {section0_html}
    """

    # Build complete HTML document
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Opponent Intelligence Report</title>
        {get_all_styles()}
    </head>
    <body>
        <div class="a4-container">
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
    parser.add_argument('--player-id', type=int, default=None, help='Optional: Player ID to include in report')

    args = parser.parse_args()

    team_name = args.team
    season = args.season
    league = args.league
    competition_id = args.competition_id
    season_id = args.season_id
    player_id = args.player_id

    if player_id:
        print(f"Generating opposition report for {team_name} in {season_id}: {season} ({competition_id}: {league}), Player ID: {player_id}...")
    else:
        print(f"Generating opposition report for {team_name} in {season_id}: {season} ({competition_id}: {league})...")

    # Get aggregates from event data
    all_metrics = get_aggregates_for_team(season)
    statsbomb_team_metrics = get_team_stats(competition_id, season_id, team_name)
    #print(f"✓ Loaded team metrics for {team_name} from StatsBomb data provider.")
    #print(statsbomb_team_metrics)
    if player_id:
        statsbomb_player_metrics = get_player_stats(competition_id, season_id, player_id)  # Get stats for the specified player
    #print(f"✓ Loaded player metrics from StatsBomb data provider.")
    #print(statsbomb_player_metrics.get('player_season_minutes'))
    
    # Find team metrics by looping through and matching team_name field
    team_metrics = {}
    for layer_name, layer_data in all_metrics.items():
        if isinstance(layer_data, dict):
            for team_id, team_data in layer_data.items():
                if isinstance(team_data, dict) and team_data.get('team_name') == team_name:
                    team_metrics = team_data
                    break
    team_metrics['season'] = season  # Ensure season is included
    team_metrics['total_teams'] = len(all_metrics.get('xg', []))
    team_metrics['league'] = league  # Include league information
    # Render the complete report with metrics
    html_output = render_complete_report(team_metrics, statsbomb_team_metrics)

    # Save HTML output to file
    report_path = Path(__file__).parent / 'report.html'
    with open(report_path, 'w') as f:
        f.write(html_output)

    print(f"✓ Report saved to {report_path}")


    # Output HTML to stdout for direct frontend display
    # Use a marker to separate from other output
    print("\n<<<HTML_START>>>")
    #print(html_output)
    print("<<<HTML_END>>>")
