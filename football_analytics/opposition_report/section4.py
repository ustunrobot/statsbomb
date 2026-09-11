#!/usr/bin/env python3
"""Section 4: Shot type analysis with pie chart."""

import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.metrics import Metric

section_data = {}

section_data['Team'] = "Port Vale FC"

# Organize metrics by shot type categories
section_data['Metrics'] = {
    # Direct shots
    'direct_corner': Metric(value=2.3, value_pg=0.46, percentile=58.0, percentile_order=10, percentile_total=24, sample_size=5, average=0.46, z_score=0.4),
    'direct_free_kick': Metric(value=1.8, value_pg=0.36, percentile=52.0, percentile_order=12, percentile_total=24, sample_size=5, average=0.36, z_score=0.1),
    'direct_kick_off': Metric(value=0.5, value_pg=0.1, percentile=35.0, percentile_order=16, percentile_total=24, sample_size=5, average=0.1, z_score=-0.9),
    'penalty': Metric(value=1.2, value_pg=0.24, percentile=48.0, percentile_order=13, percentile_total=24, sample_size=5, average=0.24, z_score=-0.2),

    # Set piece shots
    'set_piece_corner': Metric(value=3.5, value_pg=0.7, percentile=65.0, percentile_order=9, percentile_total=24, sample_size=5, average=0.7, z_score=0.6),
    'set_piece_throw_in': Metric(value=0.8, value_pg=0.16, percentile=42.0, percentile_order=14, percentile_total=24, sample_size=5, average=0.16, z_score=-0.6),
    'set_piece_free_kick': Metric(value=2.1, value_pg=0.42, percentile=55.0, percentile_order=11, percentile_total=24, sample_size=5, average=0.42, z_score=0.2),

    # Open play
    'open_play': Metric(value=5.8, value_pg=1.16, percentile=68.0, percentile_order=8, percentile_total=24, sample_size=5, average=1.16, z_score=0.7),
}

# Additional metrics
section_data['Additional_Metrics'] = {
    'header': Metric(value=28, value_pg=5.6, percentile=72.0, percentile_order=7, percentile_total=24, sample_size=5, average=5.6, z_score=0.8),
    'outbox': Metric(value=12.5, value_pg=2.5, percentile=55.0, percentile_order=11, percentile_total=24, sample_size=5, average=2.5, z_score=0.2),
    'one_on_one': Metric(value=7.2, value_pg=1.44, percentile=61.0, percentile_order=10, percentile_total=24, sample_size=5, average=1.44, z_score=0.5),
}

# Derived metrics
section_data['Derived_Metrics'] = {
    'shot_volume': Metric(value=48, value_pg=9.6, percentile=68.0, percentile_order=8, percentile_total=24, sample_size=5, average=9.6, z_score=0.6),
    'shot_quality': Metric(value=0.26, value_pg=0.052, percentile=62.0, percentile_order=9, percentile_total=24, sample_size=5, average=0.052, z_score=0.4),
    'finishing': Metric(value=0.95, value_pg=0.19, percentile=58.0, percentile_order=10, percentile_total=24, sample_size=5, average=0.19, z_score=0.3),
}


def create_pie_chart(section_data: dict) -> str:
    """Create an SVG pie chart showing shot type distribution."""
    metrics = section_data.get('Metrics', {})

    # Calculate totals by category
    direct_total = metrics['direct_corner'].value + metrics['direct_free_kick'].value + metrics['direct_kick_off'].value + metrics['penalty'].value
    set_piece_total = metrics['set_piece_corner'].value + metrics['set_piece_throw_in'].value + metrics['set_piece_free_kick'].value
    open_play_total = metrics['open_play'].value

    grand_total = direct_total + set_piece_total + open_play_total

    # Color palettes
    direct_colors = ['#17a2b8', '#117a8b', '#0c5460']  # Teal shades
    set_piece_colors = ['#c85a3e', '#a84827', '#8b3a1f']  # Brick/red shades
    open_play_color = '#6c757d'  # Gray

    # Chart dimensions
    size = 320
    center_x = size / 2
    center_y = size / 2
    radius = 90

    def calculate_pie_slice(start_angle, percentage, color):
        """Calculate SVG path for pie slice."""
        slice_angle = (percentage / 100) * 360
        end_angle = start_angle + slice_angle

        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)

        x1 = center_x + radius * math.cos(start_rad)
        y1 = center_y + radius * math.sin(start_rad)
        x2 = center_x + radius * math.cos(end_rad)
        y2 = center_y + radius * math.sin(end_rad)

        large_arc = 1 if slice_angle > 180 else 0

        path = f"M {center_x} {center_y} L {x1} {y1} A {radius} {radius} 0 {large_arc} 1 {x2} {y2} Z"
        return f'<path d="{path}" fill="{color}" stroke="white" stroke-width="2"/>'

    # Build SVG
    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" class="pie-chart">
        <!-- Background with border -->
        <rect width="{size}" height="{size}" fill="white" stroke="#d9d9d9" stroke-width="1"/>

        <!-- Pie slices -->
    """

    current_angle = 0

    # Direct shots
    direct_pct = (direct_total / grand_total) * 100
    svg += calculate_pie_slice(current_angle, direct_pct, direct_colors[0])
    current_angle += (direct_pct / 100) * 360

    # Set pieces
    set_piece_pct = (set_piece_total / grand_total) * 100
    svg += calculate_pie_slice(current_angle, set_piece_pct, set_piece_colors[0])
    current_angle += (set_piece_pct / 100) * 360

    # Open play
    open_play_pct = (open_play_total / grand_total) * 100
    svg += calculate_pie_slice(current_angle, open_play_pct, open_play_color)

    # Center circle (donut effect)
    svg += f'<circle cx="{center_x}" cy="{center_y}" r="40" fill="white"/>'

    # Legend text in center
    svg += f"""
        <text x="{center_x}" y="{center_y - 5}" font-family="Inter, sans-serif" font-size="14" font-weight="700" fill="#0f1923" text-anchor="middle">{grand_total:.1f}</text>
        <text x="{center_x}" y="{center_y + 12}" font-family="Inter, sans-serif" font-size="10" fill="#999" text-anchor="middle">Total xG</text>

        <!-- Legend -->
        <rect x="20" y="230" width="12" height="12" fill="{direct_colors[0]}" rx="2"/>
        <text x="36" y="239" font-family="Inter, sans-serif" font-size="10" font-weight="500" fill="#0f1923">Direct ({direct_pct:.0f}%)</text>

        <rect x="20" y="250" width="12" height="12" fill="{set_piece_colors[0]}" rx="2"/>
        <text x="36" y="259" font-family="Inter, sans-serif" font-size="10" font-weight="500" fill="#0f1923">Set Piece ({set_piece_pct:.0f}%)</text>

        <rect x="20" y="270" width="12" height="12" fill="{open_play_color}" rx="2"/>
        <text x="36" y="279" font-family="Inter, sans-serif" font-size="10" font-weight="500" fill="#0f1923">Open Play ({open_play_pct:.0f}%)</text>
    </svg>
    """
    return svg


def render_metrics_cards(metrics_dict: dict, background_class: str = "", label_override: dict = None) -> str:
    """Render metrics in card format (similar to section2).

    Args:
        metrics_dict: Dictionary of metrics to render
        background_class: CSS class for background styling
        label_override: Dictionary to override metric names for display
    """
    cards_html = ""
    for metric_name, metric in metrics_dict.items():
        z_score = metric.z_score
        # Map z-score from -2 to +2 range to 0-100% position
        bar_end_position = ((z_score + 2) / 4) * 100
        bar_end_position = max(0, min(100, bar_end_position))

        # Bar starts at 50% (average/center) and extends to z-score position
        bar_start = 50
        bar_width = abs(bar_end_position - bar_start)
        bar_left = min(bar_start, bar_end_position)

        # Determine color based on z-score
        if z_score < -0.2:
            bar_color = "#e74c3c"  # Red
        elif z_score > 0.2:
            bar_color = "#27ae60"  # Green
        else:
            bar_color = "#666666"  # Dark gray

        # Get display name
        display_name = label_override.get(metric_name, metric_name.upper()) if label_override else metric_name.upper()

        card_class = f"metric-card {background_class}" if background_class else "metric-card"
        cards_html += f"""
            <div class="{card_class}">
                <div class="metric-card-name">{display_name}</div>
                <div class="metric-card-value">{metric.value:.2f}</div>
                <div class="metric-card-zscore">{z_score:.2f} ({metric.percentile:.0f}%)</div>
                <div class="metric-card-bar">
                    <div class="metric-card-bar-background">
                        <div class="metric-card-bar-center"></div>
                        <div class="metric-card-bar-fill" style="left: {bar_left}%; width: {bar_width}%; background-color: {bar_color};"></div>
                    </div>
                </div>
            </div>
        """
    return cards_html


def render_additional_metrics(additional_metrics: dict) -> str:
    """Render additional metrics in card format (similar to section2)."""
    return render_metrics_cards(additional_metrics)


def render_derived_metrics_cards(metrics_dict: dict, label_override: dict = None) -> str:
    """Render derived metrics with distinct colors for each metric.

    Args:
        metrics_dict: Dictionary of metrics to render
        label_override: Dictionary to override metric names for display
    """
    color_mapping = {
        'shot_volume': 'metric-card-light-teal',
        'shot_quality': 'metric-card-light-brick',
        'finishing': 'metric-card-light-gray-custom'
    }

    cards_html = ""
    for metric_name, metric in metrics_dict.items():
        z_score = metric.z_score
        bar_end_position = ((z_score + 2) / 4) * 100
        bar_end_position = max(0, min(100, bar_end_position))

        bar_start = 50
        bar_width = abs(bar_end_position - bar_start)
        bar_left = min(bar_start, bar_end_position)

        if z_score < -0.2:
            bar_color = "#e74c3c"
        elif z_score > 0.2:
            bar_color = "#27ae60"
        else:
            bar_color = "#666666"

        display_name = label_override.get(metric_name, metric_name.upper()) if label_override else metric_name.upper()
        background_class = color_mapping.get(metric_name, "metric-card")
        card_class = f"metric-card {background_class}"

        cards_html += f"""
            <div class="{card_class}">
                <div class="metric-card-name">{display_name}</div>
                <div class="metric-card-value">{metric.value:.2f}</div>
                <div class="metric-card-zscore">{z_score:.2f} ({metric.percentile:.0f}%)</div>
                <div class="metric-card-bar">
                    <div class="metric-card-bar-background">
                        <div class="metric-card-bar-center"></div>
                        <div class="metric-card-bar-fill" style="left: {bar_left}%; width: {bar_width}%; background-color: {bar_color};"></div>
                    </div>
                </div>
            </div>
        """
    return cards_html


def render_shot_type_section(section_data: dict) -> str:
    """Render section 4 with pie chart and details side-by-side."""
    pie_svg = create_pie_chart(section_data)
    metrics = section_data.get('Metrics', {})

    # Build right square content with details
    details_html = """
        <div class="shot-type-details-box">
            <div class="details-section">
                <div class="details-header">Direct Shots</div>
                <div class="details-items">
    """
    for metric_name in ['direct_corner', 'direct_free_kick', 'direct_kick_off', 'penalty']:
        metric = metrics[metric_name]
        label_short = metric_name.replace('_', ' ').replace('direct ', 'D.').title()
        details_html += f"""
                    <div class="detail-item">
                        <div class="detail-item-label">{label_short}</div>
                        <div class="detail-item-value"><span class="detail-item-percentile">{metric.percentile:.0f}%</span>{metric.value:.1f}</div>
                    </div>
        """
    details_html += """
                </div>
            </div>

            <div class="details-section">
                <div class="details-header">Set Pieces</div>
                <div class="details-items">
    """
    for metric_name in ['set_piece_corner', 'set_piece_throw_in', 'set_piece_free_kick']:
        metric = metrics[metric_name]
        label_short = metric_name.replace('set_piece_', 'SP ').replace('_', ' ').title()
        details_html += f"""
                    <div class="detail-item">
                        <div class="detail-item-label">{label_short}</div>
                        <div class="detail-item-value"><span class="detail-item-percentile">{metric.percentile:.0f}%</span>{metric.value:.1f}</div>
                    </div>
        """
    details_html += """
                </div>
            </div>

            <div class="details-section">
                <div class="details-header">Open Play</div>
                <div class="details-items">
    """
    metric = metrics['open_play']
    details_html += f"""
                    <div class="detail-item">
                        <div class="detail-item-label">OP</div>
                        <div class="detail-item-value"><span class="detail-item-percentile">{metric.percentile:.0f}%</span>{metric.value:.1f}</div>
                    </div>
                </div>
            </div>
        </div>
    """

    # Render additional metrics
    additional_metrics_html = render_additional_metrics(section_data.get('Additional_Metrics', {}))

    # Render derived metrics with custom colors per metric
    derived_label_override = {
        'shot_volume': 'Shot Volume',
        'shot_quality': 'Shot Quality',
        'finishing': 'Finishing'
    }
    derived_metrics_html = render_derived_metrics_cards(
        section_data.get('Derived_Metrics', {}),
        label_override=derived_label_override
    )

    html = f"""
    <section class="shot-type-section">
        <div class="section-container">
            <h2 class="section-title">Attacking Breakdown</h2>
            <p class="section-subtitle">xGF breakdown by shot type for {section_data.get('Team', 'Team')}</p>

            <div class="shot-type-container">
                <div class="chart-wrapper">
                    {pie_svg}
                </div>
                {details_html}
            </div>

            <div class="additional-metrics-section">
                <h3 class="additional-metrics-title">Additional xGF Metrics</h3>
                <div class="additional-metrics-grid">
                    {additional_metrics_html}
                </div>
            </div>

            <div class="additional-metrics-section">
                <h3 class="additional-metrics-title">Derived Metrics</h3>
                <div class="additional-metrics-grid">
                    {derived_metrics_html}
                </div>
            </div>
        </div>
    </section>
    """
    return html


def get_styles() -> str:
    """Return CSS styles for section 4."""
    return """
    <style>
    .shot-type-section {
      padding: 40px 48px;
      background: white;
      border-top: 1px solid #e5e5e5;
      page-break-after: always;
    }

    .section-container {
      max-width: 1000px;
    }

    .section-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 24px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 4px;
    }

    .section-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: #999;
      margin-bottom: 24px;
    }

    .shot-type-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      align-items: start;
    }

    .chart-wrapper {
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .pie-chart {
      max-width: 100%;
      height: auto;
    }

    .shot-type-details-box {
      background: white;
      padding: 0;
      display: flex;
      flex-direction: column;
      gap: 8px;
      height: 320px;
      overflow-y: auto;
    }

    .details-section {
      display: flex;
      flex-direction: column;
      gap: 4px;
      flex: 1;
    }

    .details-header {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 12px;
      font-weight: 600;
      color: #333;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin: 0;
      padding-top: 4px;
    }

    .details-items {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .detail-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      padding: 3px 0;
    }

    .detail-item-label {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 10px;
      color: #666;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 500;
      flex: 1;
    }

    .detail-item-value {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 12px;
      font-weight: 600;
      color: #0f1923;
      text-align: right;
      white-space: nowrap;
    }

    .detail-item-percentile {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 10px;
      font-weight: 500;
      color: #999;
      display: inline;
      margin-right: 2px;
    }

    .additional-metrics-section {
      margin-top: 24px;
      padding-top: 16px;
      border-top: 1px solid #e5e5e5;
    }

    .additional-metrics-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 14px;
      font-weight: 600;
      color: var(--ink);
      margin: 0 0 16px 0;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .additional-metrics-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }

    .metric-card {
      border: 1px solid #d9d9d9;
      border-radius: 6px;
      padding: 12px;
      background: white;
    }

    .metric-card.metric-card-light-gray {
      background: #e8fbfd;
    }

    .metric-card.metric-card-light-teal {
      background: #ecfbfd;
      border: none;
    }

    .metric-card.metric-card-light-brick {
      background: #fdf2ed;
      border: none;
    }

    .metric-card.metric-card-light-gray-custom {
      background: #f5f7fa;
      border: none;
    }

    .metric-card-name {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 9px;
      color: #999;
      font-weight: 500;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .metric-card-value {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 16px;
      font-weight: 700;
      color: #0f1923;
      margin-bottom: 6px;
    }

    .metric-card-zscore {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 10px;
      color: #999;
      margin-bottom: 8px;
    }

    .metric-card-bar {
      height: 18px;
      display: flex;
      align-items: center;
      position: relative;
    }

    .metric-card-bar-background {
      width: 100%;
      height: 5px;
      background: #e5e5e5;
      border-radius: 3px;
      position: relative;
    }

    .metric-card-bar-center {
      position: absolute;
      left: 50%;
      top: -3px;
      width: 1.5px;
      height: 11px;
      background: #999;
      transform: translateX(-50%);
    }

    .metric-card-bar-fill {
      position: absolute;
      top: 0;
      height: 5px;
      border-radius: 3px;
      transition: all 0.3s ease;
    }
    </style>
    """


if __name__ == "__main__":
    # Test the function
    html_output = render_shot_type_section(section_data)
    print(html_output)
