"""PAGE 6: Last 5 Games Trends with radar chart."""

from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak, Spacer

from ..report_common.report_definition import get_styles, letter_space, COLOR_RED_TINT, COLOR_HEADER_TEXT, COLOR_BG_SECTION, COLOR_BORDER_LIGHT
from ..report_common.radar import create_player_radar_chart
from ..report_common.barchart import create_barchart
from ..report_common.report_definition import ChartValue, ChartParams



def create_page_6_last5_analysis(story, page_width: float, team: str, stats, team_stats_def):
    """Create PAGE 4: Out of Possession with mini header."""
    styles = get_styles()

    # Mini header with red background
    mini_header_data = [
        [
            Paragraph(
                f"{letter_space('Last 5 Games Trends')}",
                styles['SectionLabelRed']
            ),
        ],
    ]

    mini_header_table = Table(mini_header_data, colWidths=[page_width])
    mini_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_RED_TINT),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_HEADER_TEXT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 48),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('BORDERS', (0, 0), (-1, -1), 0),
    ]))

    story.append(mini_header_table)

    story.append(Spacer(1, 0.6 * inch))

    # Create radar value instances for each metric
    radar_values = {
        'Goals/90': ChartValue(chart_val=0.49, avg_val=0.23, max_val=0.7, min_val=0.0, percentile=70, percentile_total=78),
        'Dribbles/90': ChartValue(chart_val=1.79, avg_val=0.98, max_val=2.2, min_val=0.0, percentile=65, percentile_total=78),
        'OBV/90': ChartValue(chart_val=0.25, avg_val=0.18, max_val=0.5, min_val=0.0, percentile=58, percentile_total=78),
        'Test/90': ChartValue(chart_val=5.0, avg_val=12.2, max_val=25.8, min_val=0.0, percentile=6, percentile_total=78),
        'Pressures': ChartValue(chart_val=15.14, avg_val=14.6, max_val=30.0, min_val=0.0, percentile=45, percentile_total=78),
        'xA/90': ChartValue(chart_val=0.12, avg_val=0.13, max_val=0.2, min_val=0.0, percentile=34, percentile_total=78),
        'xG/90': ChartValue(chart_val=0.22, avg_val=0.33, max_val=0.5, min_val=0.0, percentile=22, percentile_total=78),
        'Passes/90': ChartValue(chart_val=12.0, avg_val=18.2, max_val=28.8, min_val=0.0, percentile=20, percentile_total=78),
        'Ratio/90': ChartValue(chart_val=3.0, avg_val=10.2, max_val=15.8, min_val=0.0, percentile=10, percentile_total=78),
        
    }

    # Create radar params
    radar_params = ChartParams(
        chart_type="LineGrid",        
        outer_table_size=160,
        #outer_table_bg_color=COLOR_BG_SECTION,
        outer_table_bg_color='#f8f8f8',
        #outer_table_border_color=COLOR_BORDER_LIGHT,
        outer_table_border_color='#DDDDDD',        
        title='Player Statistics',        
        values=radar_values
    )

    radar_table = create_player_radar_chart(styles=styles, radar_params=radar_params)
    story.append(radar_table)

    story.append(Spacer(1, 0.6 * inch))

    # Populate barchart_values from stats data
    barchart_values = {}

    if stats and isinstance(stats, list) and len(stats) > 0:
        # Find team data using team_name field
        team_data = next((s for s in stats if s.get('team_name') == team), None)

        if not team_data and team:
            # Try case-insensitive match
            team_data = next((s for s in stats if str(s.get('team_name', '')).lower() == str(team).lower()), None)

        if team_data:
            # Get all numeric statistics from the team data (exclude non-numeric/metadata fields)
            numeric_stats = {k: v for k, v in team_data.items()
                           if isinstance(v, (int, float)) and k not in ['team_name', 'team_id', 'account_id', 'competition_id', 'season_id', 'n_events', 'n_matches', 'n_metrics']}

            # Calculate statistics across all teams
            for stat_name, stat_value in numeric_stats.items():
                # Collect values for this statistic across all teams
                all_values = [s.get(stat_name) for s in stats
                            if isinstance(s.get(stat_name), (int, float))]

                if all_values:
                    avg_val = sum(all_values) / len(all_values)
                    max_val = max(all_values)
                    min_val = min(all_values)

                    # Calculate percentile rank
                    sorted_values = sorted(all_values)
                    percentile = sum(1 for v in sorted_values if v <= stat_value)
                    percentile_total = len(all_values)

                    # Calculate standard deviation
                    variance = sum((x - avg_val) ** 2 for x in all_values) / len(all_values)
                    std_dev = variance ** 0.5

                    # Normalize max_val to avoid division by zero
                    if max_val == 0:
                        max_val = 1

                    # Look up stat definition to check if it should be used
                    stat_def = next((s for s in team_stats_def if s.get('name') == stat_name), None)
                    if stat_def:
                        should_use = stat_def.get('use') == 'Yes'
                        # Use short_name if available and not empty, otherwise fall back to stat_name
                        display_name = stat_def.get('short_name') or stat_name
                        group_name = stat_def.get('subgroup') 
                        reverse = stat_def.get('reverse') 
                    else:
                        should_use = False
                        display_name = stat_name

                    if should_use:
                        barchart_values[display_name] = ChartValue(
                            group=group_name,
                            reverse=reverse,
                            chart_val=stat_value,
                            avg_val=avg_val,
                            max_val=max_val,
                            min_val=min_val,
                            std_dev=std_dev,
                            percentile=percentile,
                            percentile_total=percentile_total
                        )

        # Sort barchart_values by group, then by display_name
        barchart_values = dict(sorted(
            barchart_values.items(),
            key=lambda x: (x[1].group or "", x[0])  # Sort by group, then by display_name
        ))

    barchart_params = ChartParams(
        chart_type="LineGrid",
        outer_table_size=200,        
        outer_table_bg_color='#ffffff',
        outer_table_border_color='#cccccc',        
        title='Team Statistics',        
        values=barchart_values
    )

    barchart_table = create_barchart(styles=styles, chart_params=barchart_params)
    story.append(barchart_table)
    

    story.append(PageBreak())
