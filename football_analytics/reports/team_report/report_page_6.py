"""PAGE 6: Last 5 Games Trends with radar chart."""

from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak, Spacer

from ..report_common.report_definition import get_styles, letter_space, COLOR_RED_TINT, COLOR_HEADER_TEXT, COLOR_BG_SECTION, COLOR_BORDER_LIGHT
from ..report_common.radar import create_player_radar_chart
from ..report_common.barchart import create_barchart
from ..report_common.report_definition import ChartValue, ChartParams



def create_page_6_last5_analysis(story, page_width: float):
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
        'Goals/90': ChartValue(chart_val=0.49, avg_val=0.23, max_val=0.7, percentile=4, percentile_total=78),
        'Dribbles/90': ChartValue(chart_val=1.79, avg_val=0.98, max_val=2.2, percentile=9, percentile_total=78),
        'OBV/90': ChartValue(chart_val=0.25, avg_val=0.18, max_val=0.5, percentile=20, percentile_total=78),
        'Test/90': ChartValue(chart_val=5.0, avg_val=12.2, max_val=25.8, percentile=72, percentile_total=78),
        'Pressures': ChartValue(chart_val=15.14, avg_val=14.6, max_val=30.0, percentile=31, percentile_total=78),
        'xA/90': ChartValue(chart_val=0.12, avg_val=0.13, max_val=0.2, percentile=44, percentile_total=78),
        'xG/90': ChartValue(chart_val=0.22, avg_val=0.33, max_val=0.5, percentile=54, percentile_total=78),
        'Passes/90': ChartValue(chart_val=12.0, avg_val=18.2, max_val=28.8, percentile=58, percentile_total=78),
        'Ratio/90': ChartValue(chart_val=3.0, avg_val=10.2, max_val=15.8, percentile=68, percentile_total=78),
        
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

    barchart_values = {
                'Goals/90': ChartValue(chart_val=0.49, avg_val=0.23, max_val=0.7, percentile=4, percentile_total=78),
                'Dribbles/90': ChartValue(chart_val=1.79, avg_val=0.98, max_val=2.2, percentile=9, percentile_total=78),
                'OBV/90': ChartValue(chart_val=0.25, avg_val=0.18, max_val=0.5, percentile=20, percentile_total=78),
                'Test/90': ChartValue(chart_val=5.0, avg_val=12.2, max_val=25.8, percentile=72, percentile_total=78),
                'Pressures': ChartValue(chart_val=15.14, avg_val=14.6, max_val=30.0, percentile=31, percentile_total=78),
                'xA/90': ChartValue(chart_val=0.12, avg_val=0.13, max_val=0.2, percentile=44, percentile_total=78),
                'xG/90': ChartValue(chart_val=0.22, avg_val=0.33, max_val=0.5, percentile=54, percentile_total=78),
                'Passes/90': ChartValue(chart_val=12.0, avg_val=18.2, max_val=28.8, percentile=58, percentile_total=78),
                'Ratio/90': ChartValue(chart_val=3.0, avg_val=10.2, max_val=15.8, percentile=68, percentile_total=78),
    }

    barchart_params = ChartParams(
        chart_type="LineGrid",
        outer_table_size=200,        
        outer_table_bg_color='#ffffff',
        outer_table_border_color='#cccccc',        
        title='Player Statistics',        
        values=barchart_values
    )

    barchart_table = create_barchart(styles=styles, chart_params=barchart_params)
    story.append(barchart_table)
    

    story.append(PageBreak())
