#!/usr/bin/env python3
"""Section 5: Defending metrics."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.metrics import Metric

section_data = {}

section_data['Team'] = "Port Vale FC"
section_data['Metrics'] = {
    'xga': Metric(value=8.3, value_pg=1.66, percentile=45.0, percentile_order=13, percentile_total=24, sample_size=5, average=1.66, z_score=-0.4),
    'shots_conceded': Metric(value=35, value_pg=7.0, percentile=55.0, percentile_order=12, percentile_total=24, sample_size=5, average=7.0, z_score=0.7),
    'goals_conceded': Metric(value=6, value_pg=1.2, percentile=48.0, percentile_order=13, percentile_total=24, sample_size=5, average=1.2, z_score=-0.1),
    'ppda': Metric(value=12.5, value_pg=2.5, percentile=62.0, percentile_order=9, percentile_total=24, sample_size=5, average=2.5, z_score=0.5),
    'xg_per_shot': Metric(value=0.24, value_pg=0.048, percentile=58.0, percentile_order=10, percentile_total=24, sample_size=5, average=0.048, z_score=0.3),
}

# Defensive actions breakdown - first rectangle
section_data['Defensive_Actions_1'] = {
    'tackles': Metric(value=120, value_pg=24.0, percentile=68.0, percentile_order=8, percentile_total=24, sample_size=5, average=24.0, z_score=0.7),
    'interceptions': Metric(value=45, value_pg=9.0, percentile=62.0, percentile_order=9, percentile_total=24, sample_size=5, average=9.0, z_score=0.5),
    'blocks': Metric(value=28, value_pg=5.6, percentile=55.0, percentile_order=11, percentile_total=24, sample_size=5, average=5.6, z_score=0.2),
    'clearances': Metric(value=95, value_pg=19.0, percentile=72.0, percentile_order=7, percentile_total=24, sample_size=5, average=19.0, z_score=0.8),
    'aerial_wins': Metric(value=38, value_pg=7.6, percentile=58.0, percentile_order=10, percentile_total=24, sample_size=5, average=7.6, z_score=0.3),
    'pressures': Metric(value=185, value_pg=37.0, percentile=65.0, percentile_order=8, percentile_total=24, sample_size=5, average=37.0, z_score=0.6),
}

# Defensive efficiency - second rectangle
section_data['Defensive_Actions_2'] = {
    'tackles_won': Metric(value=85, value_pg=17.0, percentile=70.0, percentile_order=7, percentile_total=24, sample_size=5, average=17.0, z_score=0.75),
    'pressure_success': Metric(value=0.42, value_pg=0.084, percentile=60.0, percentile_order=10, percentile_total=24, sample_size=5, average=0.084, z_score=0.4),
    'pass_interceptions': Metric(value=32, value_pg=6.4, percentile=68.0, percentile_order=8, percentile_total=24, sample_size=5, average=6.4, z_score=0.65),
    'defensive_errors': Metric(value=4, value_pg=0.8, percentile=35.0, percentile_order=16, percentile_total=24, sample_size=5, average=0.8, z_score=-0.8),
    'fouls_committed': Metric(value=28, value_pg=5.6, percentile=48.0, percentile_order=13, percentile_total=24, sample_size=5, average=5.6, z_score=-0.1),
    'clearances_accurate': Metric(value=72, value_pg=14.4, percentile=75.0, percentile_order=6, percentile_total=24, sample_size=5, average=14.4, z_score=0.9),
}


def render_defensive_actions_simple(metric) -> str:
    """Render a single defensive action metric card without bar."""
    label = metric.__class__.__name__.split('.')[-1]
    z_score = metric.z_score

    if z_score < -0.2:
        value_color = "#e74c3c"
    elif z_score > 0.2:
        value_color = "#27ae60"
    else:
        value_color = "#666666"

    return f"""
    <div class="defensive-action-card">
        <div class="def-card-name">{label}</div>
        <div class="def-card-value" style="color: {value_color};">{metric.value:.2f}</div>
        <div class="def-card-percentile">{metric.percentile:.0f}%</div>
    </div>
    """


def create_flow_arrow() -> str:
    """Create a downward arrow SVG for flow visualization."""
    return """
    <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" class="flow-arrow">
        <defs>
            <marker id="arrowhead" markerWidth="5" markerHeight="5" refX="2.5" refY="2.5" orient="auto">
                <polygon points="0,0 5,2.5 0,5" fill="#999"/>
            </marker>
        </defs>
        <line x1="20" y1="14" x2="20" y2="26" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
    </svg>
    """


def render_defending_section(section_data: dict) -> str:
    """Render defending metrics in card grid."""
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

    # Combine and reorganize defensive actions for grouped layout
    all_actions = {**section_data.get('Defensive_Actions_1', {}), **section_data.get('Defensive_Actions_2', {})}
    actions_list = list(all_actions.items())

    # Color palette with shades for 4 colors (original, 1 shade lighter, 2 shades lighter)
    colors = {
        0: [  # Teal
            '#17a2b8',  # Original
            '#35c0d6',  # 1 shade lighter
            '#53def4'   # 2 shades lighter
        ],
        1: [  # Brick/Red
            '#c85a3e',  # Original
            '#e6785c',  # 1 shade lighter
            '#ff967a'   # 2 shades lighter
        ],
        2: [  # Gray
            '#6c757d',  # Original
            '#8a939b',  # 1 shade lighter
            '#a8b1b9'   # 2 shades lighter
        ],
        3: [  # Mustard
            '#D4A017',  # Original
            '#f2be35',  # 1 shade lighter
            '#ffdc53'   # 2 shades lighter
        ]
    }

    # Organize into 2 groups of 2 columns x 3 rows
    group_1_row_1 = ""
    group_1_row_2 = ""
    group_1_row_3 = ""
    group_2_row_1 = ""
    group_2_row_2 = ""
    group_2_row_3 = ""

    for i, (metric_name, metric) in enumerate(actions_list):
        # Get the display name from metric_name
        label = metric_name.replace('_', ' ').title()

        # Assign colors by column within each group
        if i < 6:  # Group 1
            color_idx = i % 2  # 0 for column 1 (Teal), 1 for column 2 (Brick)
        else:  # Group 2
            color_idx = 2 + (i % 2)  # 2 for column 1 (Gray), 3 for column 2 (Mustard)

        # Determine row shade (0=original, 1=1 shade lighter, 2=2 shades lighter)
        if i < 2 or (i >= 6 and i < 8):
            shade_idx = 0  # Row 1: Original color
        elif i < 4 or (i >= 8 and i < 10):
            shade_idx = 1  # Row 2: 1 shade lighter
        else:
            shade_idx = 2  # Row 3: 2 shades lighter

        bg_color = colors[color_idx][shade_idx]
        text_color = 'white'

        card_html = f"""
    <div class="defensive-action-card" style="background: {bg_color}; color: {text_color};">
        <div class="def-card-name">{label}</div>
        <div class="def-card-value">{metric.value:.2f}</div>
        <div class="def-card-percentile">{metric.percentile:.0f}%</div>
    </div>
        """

        # Group 1: columns 1-2 (metrics 0-5)
        if i < 2:
            group_1_row_1 += card_html
        elif i < 4:
            group_1_row_2 += card_html
        elif i < 6:
            group_1_row_3 += card_html
        # Group 2: columns 3-4 (metrics 6-11)
        elif i < 8:
            group_2_row_1 += card_html
        elif i < 10:
            group_2_row_2 += card_html
        else:
            group_2_row_3 += card_html

    html = f"""
    <section class="defending-section">
        <div class="section-container">
            <h2 class="section-title">Defending</h2>
            <p class="section-subtitle">Defensive metrics for {section_data.get('Team', 'Team')}</p>

            <div class="defending-metrics-grid">
                {cards_html}
            </div>

            <div class="defensive-flow-container">
                <div class="defensive-group-container">
                    <div class="defensive-group-title">Overall Pressure</div>
                    <div class="defensive-group-flex">
                        <div class="defensive-flow-row">
                            {group_1_row_1}
                        </div>
                        <div class="defensive-flow-row">
                            {group_1_row_2}
                        </div>
                        <div class="defensive-flow-row">
                            {group_1_row_3}
                        </div>
                    </div>
                </div>
                <div class="defensive-group-container">
                    <div class="defensive-group-title">Final-Half Pressure</div>
                    <div class="defensive-group-flex">
                        <div class="defensive-flow-row">
                            {group_2_row_1}
                        </div>
                        <div class="defensive-flow-row">
                            {group_2_row_2}
                        </div>
                        <div class="defensive-flow-row">
                            {group_2_row_3}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """
    return html


def get_styles() -> str:
    """Return CSS styles for section 5."""
    return """
    <style>
    .defending-section {
      padding: 40px 48px;
      background: white;
      border-top: 1px solid #e5e5e5;
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

    .defending-metrics-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
      margin-bottom: 24px;
    }

    .defensive-flow-container {
      margin-top: 32px;
      padding-top: 24px;
      border-top: 1px solid #e5e5e5;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }

    .defensive-group-container {
      border: 2px solid #d9d9d9;
      border-radius: 8px;
      padding: 12px;
    }

    .defensive-group-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 14px;
      font-weight: 600;
      color: var(--ink);
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .defensive-group-flex {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .defensive-flow-row {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 9px;
      justify-content: start;
    }

    .defensive-flow-arrow-row {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 9px;
      justify-content: start;
    }

    .defensive-action-card {
      border-radius: 6px;
      padding: 12px;
      text-align: center;
    }

    .def-card-name {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 9px;
      font-weight: 500;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      opacity: 0.85;
    }

    .def-card-value {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 4px;
    }

    .def-card-percentile {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 9px;
      opacity: 0.8;
    }

    .flow-arrow {
      display: flex;
      justify-content: center;
      align-items: center;
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
    </style>
    """


if __name__ == "__main__":
    # Test the function
    html_output = render_defending_section(section_data)
    print(html_output)
