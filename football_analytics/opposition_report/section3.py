#!/usr/bin/env python3
"""Section 3: Team metrics radar chart."""

import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.metrics import Metric

section_data = {}

section_data['Team'] = "Port Vale FC"
section_data['Metrics'] = {
    'xgf': Metric(value=12.5, value_pg=2.5, percentile=65.0, percentile_order=10, percentile_total=24, sample_size=5, average=2.5, z_score=0.5),
    'xga': Metric(value=8.3, value_pg=1.66, percentile=45.0, percentile_order=13, percentile_total=24, sample_size=5, average=1.66, z_score=-0.4),
    'shots': Metric(value=48, value_pg=9.6, percentile=72.0, percentile_order=8, percentile_total=24, sample_size=5, average=9.6, z_score=0.2),
    'goals': Metric(value=8, value_pg=1.6, percentile=58.0, percentile_order=11, percentile_total=24, sample_size=5, average=1.6, z_score=1.5),
    'op_shots': Metric(value=35, value_pg=7.0, percentile=55.0, percentile_order=12, percentile_total=24, sample_size=5, average=7.0, z_score=0.7),
    'op_xga': Metric(value=10.2, value_pg=2.04, percentile=38.0, percentile_order=15, percentile_total=24, sample_size=5, average=2.04, z_score=-0.9),
    'possession': Metric(value=285, value_pg=57.0, percentile=62.0, percentile_order=9, percentile_total=24, sample_size=5, average=57.0, z_score=0.6),
    'pass_completion': Metric(value=420, value_pg=84.0, percentile=70.0, percentile_order=7, percentile_total=24, sample_size=5, average=84.0, z_score=1.2),
}

# Sample data for 24 teams with xgf and xga z-scores
teams_comparison = [
    {"name": "Port Vale FC", "xgf_z": 0.5, "xga_z": -0.4, "is_main": True},
    {"name": "Team A", "xgf_z": 1.5, "xga_z": -1.2},
    {"name": "Team B", "xgf_z": -0.8, "xga_z": 0.6},
    {"name": "Team C", "xgf_z": 0.2, "xga_z": -0.8},
    {"name": "Team D", "xgf_z": -1.0, "xga_z": 1.0},
    {"name": "Team E", "xgf_z": 1.2, "xga_z": 0.3},
    {"name": "Team F", "xgf_z": -0.5, "xga_z": -1.5},
    {"name": "Team G", "xgf_z": 0.8, "xga_z": 0.9},
    {"name": "Team H", "xgf_z": -1.3, "xga_z": 0.2},
    {"name": "Team I", "xgf_z": 0.3, "xga_z": 1.2},
    {"name": "Team J", "xgf_z": 1.8, "xga_z": -0.6},
    {"name": "Team K", "xgf_z": -0.2, "xga_z": -0.3},
    {"name": "Team L", "xgf_z": 0.7, "xga_z": 1.5},
    {"name": "Team M", "xgf_z": -1.5, "xga_z": -0.9},
    {"name": "Team N", "xgf_z": 1.0, "xga_z": 0.0},
    {"name": "Team O", "xgf_z": -0.7, "xga_z": 0.8},
    {"name": "Team P", "xgf_z": 0.9, "xga_z": -1.1},
    {"name": "Team Q", "xgf_z": -0.4, "xga_z": -1.2},
    {"name": "Team R", "xgf_z": 1.1, "xga_z": 0.4},
    {"name": "Team S", "xgf_z": -0.9, "xga_z": 1.3},
    {"name": "Team T", "xgf_z": 0.6, "xga_z": -0.7},
    {"name": "Team U", "xgf_z": -1.2, "xga_z": 0.1},
    {"name": "Team V", "xgf_z": 1.3, "xga_z": -0.5},
    {"name": "Team W", "xgf_z": -0.6, "xga_z": 1.1},
]
section_data['Teams'] = teams_comparison


def create_scatter_chart(section_data: dict) -> str:
    """Create an SVG scatter chart for xgf vs xga z-scores."""
    teams = section_data.get('Teams', [])

    # Chart dimensions
    size = 320
    margin = 40
    chart_width = size - 2 * margin
    chart_height = size - 2 * margin
    origin_x = margin
    origin_y = size - margin

    # Map z-score (-2 to +2) to pixel position
    def z_score_to_x(z_score):
        return origin_x + ((z_score + 2) / 4) * chart_width

    def z_score_to_y(z_score):
        return origin_y - ((z_score + 2) / 4) * chart_height

    # Build SVG
    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" class="scatter-chart">
        <!-- Background with border -->
        <rect width="{size}" height="{size}" fill="white" stroke="#d9d9d9" stroke-width="1"/>

        <!-- Axes (3 shades darker) -->
        <line x1="{origin_x}" y1="{origin_y}" x2="{size - margin}" y2="{origin_y}" stroke="#808080" stroke-width="1"/>
        <line x1="{origin_x}" y1="{margin}" x2="{origin_x}" y2="{origin_y}" stroke="#808080" stroke-width="1"/>

        <!-- Grid lines at 0 (center, 2 shades darker) -->
        <line x1="{z_score_to_x(0)}" y1="{margin}" x2="{z_score_to_x(0)}" y2="{origin_y}" stroke="#bfbfbf" stroke-width="1" stroke-dasharray="2,2"/>
        <line x1="{origin_x}" y1="{z_score_to_y(0)}" x2="{size - margin}" y2="{z_score_to_y(0)}" stroke="#bfbfbf" stroke-width="1" stroke-dasharray="2,2"/>

        <!-- Axis labels (3 shades darker) -->
        <text x="{size - margin + 5}" y="{origin_y + 4}" font-family="Inter, sans-serif" font-size="9" fill="#555555">xGF</text>
        <text x="{origin_x - 20}" y="{margin - 5}" font-family="Inter, sans-serif" font-size="9" fill="#555555">xGA</text>

        <!-- Scale labels (3 shades darker) -->
        <text x="{origin_x - 3}" y="{origin_y + 12}" font-family="Inter, sans-serif" font-size="8" fill="#808080" text-anchor="end">-2</text>
        <text x="{z_score_to_x(0) + 1}" y="{origin_y + 12}" font-family="Inter, sans-serif" font-size="8" fill="#808080" text-anchor="middle">0</text>
        <text x="{size - margin + 1}" y="{origin_y + 12}" font-family="Inter, sans-serif" font-size="8" fill="#808080" text-anchor="start">+2</text>

        <text x="{origin_x - 5}" y="{margin + 2}" font-family="Inter, sans-serif" font-size="8" fill="#808080" text-anchor="end">+2</text>
        <text x="{origin_x - 5}" y="{z_score_to_y(0) + 2}" font-family="Inter, sans-serif" font-size="8" fill="#808080" text-anchor="end">0</text>
        <text x="{origin_x - 5}" y="{origin_y + 2}" font-family="Inter, sans-serif" font-size="8" fill="#808080" text-anchor="end">-2</text>
    """

    # Draw data points
    main_team = None
    for team in teams:
        x = z_score_to_x(team["xgf_z"])
        y = z_score_to_y(team["xga_z"])

        if team.get("is_main"):
            main_team = (x, y)
        else:
            # Other teams: small gray circles (1 shade darker)
            svg += f'        <circle cx="{x}" cy="{y}" r="3" fill="#999999" opacity="0.7"/>\n'

    # Draw main team last (on top) with larger size and accent color
    if main_team:
        x, y = main_team
        svg += f'        <circle cx="{x}" cy="{y}" r="6" fill="#1a4fa3" stroke="white" stroke-width="1.5"/>\n'

    svg += "    </svg>\n"
    return svg

def get_metrics_to_display(all_metrics: dict, statsbomb_team_metrics: dict) -> dict:
    metrics_to_display = {}    
    # Extract metrics from the xg layer    
    metric_keys = [
        ('team_season_passes_inside_box_pg', 'Passes into Box pG', '', '', ''),
        ('team_season_np_xg_pg', 'np xG pG', 'Non-Penalty xG', '', ''),
        ('team_season_op_shot_distance', 'Shot Distance', '', '', ''),
        ('team_season_counter_attacking_shots_pg', 'Counterattack Shots', '', '', ''),
        ('team_season_xgd_pg', 'xGD pG', '', '', ''),
        ('team_season_deep_completions_pg', 'Deep Completions pG', '', '', ''),
        ('team_season_crosses_into_box_pg', 'Crosses into Box pG', '', '', '')
        
    ]

    for key, custom_label, label2, bar_label_low, bar_label_high in metric_keys:
        # Try to get metric from all_metrics first, then fall back to statsbomb_team_metrics
        if key in all_metrics:
            metric = all_metrics.get(key)
        elif key in statsbomb_team_metrics:
            metric = statsbomb_team_metrics.get(key)
        else:
            metric = Metric.default()

        metric.label = custom_label
        metric.label2 = label2
        metric.bar_label_low = bar_label_low
        metric.bar_label_high = bar_label_high
        metrics_to_display[key] = metric
    
    return metrics_to_display

def create_radar_chart(all_metrics: dict, statsbomb_team_metrics: dict) -> str:
    """Create an SVG radar chart for metrics."""
    metrics = get_metrics_to_display(all_metrics, statsbomb_team_metrics)
    metric_names = list(metrics.keys())
    metric_count = len(metric_names)

    # Chart dimensions (reduced to fit 2 squares side-by-side)
    size = 320  # Reduced from 360 to fit two squares
    center_x = size / 2
    center_y = size / 2
    max_radius = (size / 2 - 30) * 0.7  # 30% smaller radar for space for labels
    levels = 5  # Number of concentric circles

    # Convert percentile to radius value (0-100 becomes 0-max_radius)
    def percentile_to_radius(percentile):
        return (percentile / 100) * max_radius

    # Calculate angle for each metric (starting from top, going clockwise)
    def calculate_point(metric_index, radius):
        angle = (metric_index / metric_count) * 2 * math.pi - math.pi / 2
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        return x, y

    # Build SVG
    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" class="radar-chart">
        <!-- Background with border -->
        <rect width="{size}" height="{size}" fill="white" stroke="#d9d9d9" stroke-width="1"/>

        <!-- Grid circles and levels -->
    """

    # Draw concentric circles and level labels
    for level in range(1, levels + 1):
        radius = (level / levels) * max_radius
        svg += f'        <circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="none" stroke="#e5e5e5" stroke-width="1"/>\n'
        svg += f'        <text x="{center_x + 8}" y="{center_y - radius + 5}" font-family="Inter, sans-serif" font-size="8" fill="#999">{level * 20}%</text>\n'

    # Draw radial lines
    for i in range(metric_count):
        x, y = calculate_point(i, max_radius)
        svg += f'        <line x1="{center_x}" y1="{center_y}" x2="{x}" y2="{y}" stroke="#e5e5e5" stroke-width="1"/>\n'

    # Collect points for the polygon
    points = []
    for i, (metric_name, metric) in enumerate(metrics.items()):
        radius = percentile_to_radius(metric.percentile)
        x, y = calculate_point(i, radius)
        points.append(f"{x},{y}")

    # Draw filled polygon
    points_str = " ".join(points)
    svg += f'        <polygon points="{points_str}" fill="#1a4fa3" fill-opacity="0.3" stroke="#1a4fa3" stroke-width="2"/>\n'

    # Draw data points
    for i, (metric_name, metric) in enumerate(metrics.items()):
        radius = percentile_to_radius(metric.percentile)
        x, y = calculate_point(i, radius)
        svg += f'        <circle cx="{x}" cy="{y}" r="4" fill="#1a4fa3" stroke="white" stroke-width="1.5"/>\n'

    # Draw metric labels and values
    for i, (metric_name, metric) in enumerate(metrics.items()):
        # Determine color based on z-score
        if metric.z_score < -0.2:
            value_color = "#e74c3c"  # Red
        elif metric.z_score > 0.2:
            value_color = "#27ae60"  # Green
        else:
            value_color = "#666666"  # Dark gray

        label_radius = max_radius + 25
        x, y = calculate_point(i, label_radius)

        # Use label2 if available, otherwise use label
        display_label = metric.label2 if metric.label2 else metric.label

        # Metric name
        svg += f'        <text x="{x}" y="{y}" font-family="Inter, sans-serif" font-size="10" font-weight="400" fill="#777777" text-anchor="middle" dominant-baseline="middle">{display_label}</text>\n'

        display_value = f"{metric.value_pg:.1f}" if metric.value_pg is not None else f"{metric.value:.1f}"
        # Metric value (below name)
        svg += f'        <text x="{x}" y="{y + 12}" font-family="Inter, sans-serif" font-size="9" font-weight="600" fill="{value_color}" text-anchor="middle" dominant-baseline="middle">{display_value}</text>\n'

    svg += "    </svg>\n"
    return svg


def render_radar_section(all_metrics: dict, statsbomb_team_metrics: dict) -> str:
    """Render section 3 with radar chart and scatter chart side-by-side."""
    radar_svg = create_radar_chart(all_metrics, statsbomb_team_metrics)
    scatter_svg = create_scatter_chart(all_metrics)

    html = f"""
    <section class="s3-radar-section">
        <div class="s3-section-container">
            <h2 class="s3-section-title"></h2>
            <p class="s3-section-subtitle">More attacking metrics for {all_metrics.get('team_name')}</p>

            <div class="s3-radar-container">
                <div class="s3-radar-chart-wrapper">
                    {radar_svg}
                </div>
                <div class="s3-radar-chart-wrapper">
                    {scatter_svg}
                </div>
            </div>
        </div>
    </section>
    """
    return html


def get_styles() -> str:
    """Return CSS styles for section 3."""
    return """
    <style>
    .s3-radar-section {
      padding: 40px 48px;
      background: white;
      border-top: 1px solid #e5e5e5;
      page-break-after: always;
    }

    .s3-section-container {
      max-width: 1000px;
    }

    .s3-section-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 24px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 4px;
    }

    .s3-section-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: #999;
      margin-bottom: 24px;
    }

    .s3-radar-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      align-items: start;
    }

    .s3-radar-chart-wrapper {
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .s3-radar-chart {
      max-width: 100%;
      height: auto;
    }
    </style>
    """


if __name__ == "__main__":
    # Test the function
    html_output = render_radar_section(section_data)
    print(html_output)
