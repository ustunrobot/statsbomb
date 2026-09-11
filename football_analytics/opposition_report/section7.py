#!/usr/bin/env python3
"""Section 7: Passing metrics."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.metrics import Metric

section_data = {}

section_data['Team'] = "Port Vale FC"
section_data['Metrics'] = {
    'pass_completion': Metric(value=84.2, value_pg=16.84, percentile=70.0, percentile_order=7, percentile_total=24, sample_size=5, average=16.84, z_score=1.2),
    'progressive_passes': Metric(value=42, value_pg=8.4, percentile=68.0, percentile_order=8, percentile_total=24, sample_size=5, average=8.4, z_score=0.8),
    'key_passes': Metric(value=18, value_pg=3.6, percentile=62.0, percentile_order=9, percentile_total=24, sample_size=5, average=3.6, z_score=0.5),
    'long_balls': Metric(value=28, value_pg=5.6, percentile=55.0, percentile_order=11, percentile_total=24, sample_size=5, average=5.6, z_score=0.2),
    'cross_completion': Metric(value=32.5, value_pg=6.5, percentile=48.0, percentile_order=13, percentile_total=24, sample_size=5, average=6.5, z_score=-0.1),
}

# Passing network data: Player positions and pass connections
section_data['Players'] = [
    {'name': 'GK', 'number': 1, 'position': (10, 40), 'touches': 12},
    {'name': 'LB', 'number': 3, 'position': (25, 10), 'touches': 38},
    {'name': 'CB1', 'number': 4, 'position': (30, 35), 'touches': 52},
    {'name': 'CB2', 'number': 5, 'position': (30, 65), 'touches': 48},
    {'name': 'RB', 'number': 2, 'position': (25, 75), 'touches': 42},
    {'name': 'LM', 'number': 7, 'position': (55, 15), 'touches': 35},
    {'name': 'CM1', 'number': 6, 'position': (60, 40), 'touches': 58},
    {'name': 'CM2', 'number': 8, 'position': (60, 60), 'touches': 61},
    {'name': 'RM', 'number': 11, 'position': (55, 78), 'touches': 39},
    {'name': 'LW', 'number': 9, 'position': (95, 25), 'touches': 44},
    {'name': 'ST', 'number': 10, 'position': (105, 40), 'touches': 35},
    {'name': 'RW', 'number': 12, 'position': (95, 60), 'touches': 41},
    {'name': 'Sub1', 'number': 18, 'position': (75, 25), 'touches': 18},
]

section_data['Passes'] = [
    {'from': 'GK', 'to': 'CB1', 'count': 8},
    {'from': 'GK', 'to': 'CB2', 'count': 7},
    {'from': 'CB1', 'to': 'CM1', 'count': 12},
    {'from': 'CB1', 'to': 'CM2', 'count': 10},
    {'from': 'CB2', 'to': 'CM2', 'count': 11},
    {'from': 'CB2', 'to': 'CM1', 'count': 9},
    {'from': 'CM1', 'to': 'CM2', 'count': 15},
    {'from': 'CM1', 'to': 'LW', 'count': 8},
    {'from': 'CM1', 'to': 'ST', 'count': 6},
    {'from': 'CM2', 'to': 'RW', 'count': 9},
    {'from': 'CM2', 'to': 'LW', 'count': 7},
    {'from': 'LW', 'to': 'ST', 'count': 5},
    {'from': 'ST', 'to': 'RW', 'count': 4},
    {'from': 'LB', 'to': 'CM1', 'count': 6},
    {'from': 'RB', 'to': 'CM2', 'count': 5},
]


def render_passing_section(section_data: dict) -> str:
    """Render passing metrics in card grid."""
    metrics = section_data.get('Metrics', {})

    cards_html = ""
    for metric_name, metric in metrics.items():
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

        # Format label
        label = metric_name.replace('_', ' ').title()

        cards_html += f"""
            <div class="metric-card">
                <div class="metric-card-name">{label}</div>
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

    html = f"""
    <section class="passing-section">
        <div class="section-container">
            <h2 class="section-title">Passing</h2>
            <p class="section-subtitle">Passing metrics for {section_data.get('Team', 'Team')}</p>

            <div class="passing-metrics-grid">
                {cards_html}
            </div>

            <h3 class="subsection-title">Passing Network</h3>
            <p class="section-subtitle">Player positions and pass connections</p>

            {create_passing_network_pitch(section_data)}
        </div>
    </section>
    """
    return html


def create_passing_network_pitch(section_data: dict) -> str:
    """Create SVG pitch with player positions and pass connections."""
    players = section_data.get('Players', [])
    passes = section_data.get('Passes', [])

    # Pitch dimensions: 80% of A4 width with proper ratio
    # A4 width in pixels ≈ 800px at typical display resolution
    # 80% of 800px = 640px for pitch length (x: 0-120)
    pitch_width = 640
    pitch_height = int(pitch_width * (80 / 120))  # 427px

    # Padding around the pitch
    padding = 20
    total_width = pitch_width + padding * 2
    total_height = pitch_height + padding * 2

    # Create coordinate mapping function: pitch coords (0-120, 0-80) to SVG coords
    def pitch_to_svg(x, y):
        svg_x = padding + (x / 120) * pitch_width
        svg_y = padding + (y / 80) * pitch_height
        return (svg_x, svg_y)

    # Create player name to position map
    player_map = {p['name']: p for p in players}

    # Find touch and pass count ranges for scaling
    touches = [p['touches'] for p in players]
    pass_counts = [p['count'] for p in passes]
    min_touches, max_touches = min(touches), max(touches)
    min_passes, max_passes = min(pass_counts) if pass_counts else 1, max(pass_counts) if pass_counts else 1

    # Calculate pitch markings dimensions
    # Standard football pitch: 120 units wide x 80 units tall
    px_per_unit_w = pitch_width / 120
    px_per_unit_h = pitch_height / 80

    penalty_width = int(22 * px_per_unit_w)   # 22 units
    penalty_height = int(36 * px_per_unit_h)  # 36 units
    goal_width = int(9 * px_per_unit_w)       # 9 units
    goal_height = int(12 * px_per_unit_h)     # 12 units

    center_y = pitch_height // 2
    penalty_y = int(center_y - penalty_height / 2)
    goal_y = int(center_y - goal_height / 2)

    # Draw pitch background
    svg = f"""
    <svg width="{total_width}" height="{total_height}" viewBox="0 0 {total_width} {total_height}" xmlns="http://www.w3.org/2000/svg" class="passing-network-svg">
        <!-- Pitch background -->
        <rect x="{padding}" y="{padding}" width="{pitch_width}" height="{pitch_height}" fill="#2d5a2d" stroke="#fff" stroke-width="2"/>

        <!-- Halfway line -->
        <line x1="{padding + pitch_width//2}" y1="{padding}" x2="{padding + pitch_width//2}" y2="{padding + pitch_height}" stroke="#fff" stroke-width="1"/>

        <!-- Center circle -->
        <circle cx="{padding + pitch_width//2}" cy="{padding + pitch_height//2}" r="{int(10*px_per_unit_w)}" fill="none" stroke="#fff" stroke-width="1"/>

        <!-- Center spot -->
        <circle cx="{padding + pitch_width//2}" cy="{padding + pitch_height//2}" r="2" fill="#fff"/>

        <!-- Left penalty area -->
        <rect x="{padding}" y="{padding + penalty_y}" width="{penalty_width}" height="{penalty_height}" fill="none" stroke="#fff" stroke-width="1"/>

        <!-- Right penalty area -->
        <rect x="{padding + pitch_width - penalty_width}" y="{padding + penalty_y}" width="{penalty_width}" height="{penalty_height}" fill="none" stroke="#fff" stroke-width="1"/>

        <!-- Left goal area -->
        <rect x="{padding}" y="{padding + goal_y}" width="{goal_width}" height="{goal_height}" fill="none" stroke="#fff" stroke-width="1"/>

        <!-- Right goal area -->
        <rect x="{padding + pitch_width - goal_width}" y="{padding + goal_y}" width="{goal_width}" height="{goal_height}" fill="none" stroke="#fff" stroke-width="1"/>
    """

    # Find top 5 highest pass counts
    sorted_passes = sorted(passes, key=lambda p: p.get('count', 0), reverse=True)
    top_5_indices = set()
    for i in range(min(5, len(sorted_passes))):
        top_5_indices.add(id(sorted_passes[i]))

    # Draw pass connections first (so they appear behind players)
    for pass_data in passes:
        from_player = pass_data.get('from')
        to_player = pass_data.get('to')
        count = pass_data.get('count', 1)

        if from_player in player_map and to_player in player_map:
            from_pos = player_map[from_player]['position']
            to_pos = player_map[to_player]['position']

            x1, y1 = pitch_to_svg(*from_pos)
            x2, y2 = pitch_to_svg(*to_pos)

            # Scale line width by pass count (1-5px range)
            line_width = 1 + (count - min_passes) / (max_passes - min_passes) * 4 if max_passes > min_passes else 1

            # Use bright yellow for top 5 pass counts, default gold for others
            line_color = "#ffdc53" if id(pass_data) in top_5_indices else "#D4A017"

            svg += f'        <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{line_color}" stroke-width="{line_width}" opacity="0.8"/>\n'

    # Draw players as circles
    for player in players:
        number = player.get('number', '')
        x, y = player['position']
        touches = player['touches']

        svg_x, svg_y = pitch_to_svg(x, y)

        # Scale circle radius by touches (8-20px range)
        radius = 8 + (touches - min_touches) / (max_touches - min_touches) * 12 if max_touches > min_touches else 8

        svg += f'        <circle cx="{svg_x}" cy="{svg_y}" r="{radius}" fill="#9B552D" stroke="#fff" stroke-width="2"/>\n'
        svg += f'        <text x="{svg_x}" y="{svg_y}" text-anchor="middle" dominant-baseline="middle" font-size="11" font-weight="700" fill="#fff" font-family="Inter, system-ui, sans-serif">{number}</text>\n'

    svg += '    </svg>\n'
    return svg


def get_styles() -> str:
    """Return CSS styles for section 7."""
    return """
    <style>
    .passing-section {
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

    .passing-metrics-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
    }

    .metric-card {
      border: 1px solid #d9d9d9;
      border-radius: 6px;
      padding: 11px;
      background: white;
    }

    .metric-card-name {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 9px;
      color: #999;
      font-weight: 500;
      margin-bottom: 5px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .metric-card-value {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 14px;
      font-weight: 700;
      color: #0f1923;
      margin-bottom: 5px;
    }

    .metric-card-zscore {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 9px;
      color: #999;
      margin-bottom: 8px;
    }

    .metric-card-bar {
      height: 17px;
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

    .subsection-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 16px;
      font-weight: 600;
      color: #0f1923;
      margin-top: 32px;
      margin-bottom: 4px;
    }

    .passing-network-svg {
      width: 100%;
      max-width: 680px;
      height: auto;
      display: block;
      margin-top: 16px;
    }
    </style>
    """


if __name__ == "__main__":
    # Test the function
    html_output = render_passing_section(section_data)
    print(html_output)
