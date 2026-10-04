#!/usr/bin/env python3
"""Section 10: Team metrics radar chart."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from event_based.metrics import Metric
from .charts import create_scatter_chart, create_radar_chart
from .insights_engine import InsightGenerator

def get_metrics_to_display(all_metrics: dict, statsbomb_team_metrics: dict) -> dict:
    metrics_to_display = {}    
    # Extract metrics from the xg layer    
    metric_keys = [
        ('team_season_total_dribbles_pg', 'Dribbles pG', '', '', '', False, False),
        ('carry_x_distance_total', 'Carry X distance pG', 'Vertical Carries', '', '', False, False),
        ('passes_in_final_third_total', 'F.Third Passes', '', '', '', False, False),

        ('aerial_won_ratio', 'Aerial Win Rate', '', '', '', True, False),
        ('aerial_total', 'Aerial Duels', '', '', '', False, False),
        ('high_pass_ratio', 'High Pass Ratio', '', '', '', True, False),

        ('team_season_dribble_ratio', 'Dribble Ratio', '', '', '', True, False)
        
    ]

    for key, custom_label, label2, bar_label_low, bar_label_high, show_as_percentage, reverse in metric_keys:
        # Try to get metric from all_metrics first, then fall back to statsbomb_team_metrics
        if key in all_metrics:
            metric = all_metrics.get(key)
        elif key in statsbomb_team_metrics:
            metric = statsbomb_team_metrics.get(key)
        else:
            metric = Metric.default()

        metric.label = custom_label
        metric.label2 = label2
        metric.show_as_percentage = show_as_percentage
        metric.bar_label_low = bar_label_low
        metric.bar_label_high = bar_label_high
        metric.reverse = reverse
        metrics_to_display[key] = metric
    
    return metrics_to_display



def render_radar_section(all_metrics: dict, team_metrics: dict, statsbomb_team_metrics: dict, team_name: str, league_table: dict = None) -> str:
    """Render section 10 with radar chart and scatter chart side-by-side."""
    # Extract specific team metrics from statsbomb_team_metrics (which now contains all teams)
    team_statsbomb_metrics = statsbomb_team_metrics.get(team_name, {})
    metrics = get_metrics_to_display(team_metrics, team_statsbomb_metrics)
    radar_svg = create_radar_chart(metrics)

    quadrant_labels =   {
                'top_right': 'Dominant',
                'bottom_right': 'Inefficient',
                'top_left': 'Efficient',
                'bottom_left': 'Direct'
            }
    scatter_svg = create_scatter_chart(all_metrics, statsbomb_team_metrics, team_name,
                                       x_metric_key='team_season_possession',
                                       y_metric_key='team_season_deep_progressions_pg',
                                       x_axis_label='Possession%',
                                       y_axis_label='Deep Progression',
                                       quadrants=quadrant_labels,
                                       league_table=league_table)

    # Generate possession insights from metrics
    generator = InsightGenerator(team_metrics, league_table, team_name, statsbomb_team_metrics)
    possession_insights = generator.generate_possession_insights()

    # Possession profile highlights with fallback defaults
    default_insights = [
        "Possession-based approach showing promise",
        "Ball retention metrics under evaluation",
        "Pressing intensity requires assessment",
        "Transition efficiency to be analyzed"
    ]

    # Use generated insights if available, otherwise use defaults
    while len(possession_insights) < 4:
        possession_insights.append(default_insights[len(possession_insights)])

    strength1 = possession_insights[0]
    strength2 = possession_insights[1]
    concern1 = possession_insights[2]
    concern2 = possession_insights[3]

    highlights_html = f"""
    <div class="s10-highlights-section">
        <div class="s10-highlight-item s10-highlight-strength">
            <span class="s10-highlight-label">Strength:</span>
            <span class="s10-highlight-text">{strength1}</span>
        </div>
        <div class="s10-highlight-item s10-highlight-strength">
            <span class="s10-highlight-label">Strength:</span>
            <span class="s10-highlight-text">{strength2}</span>
        </div>
        <div class="s10-highlight-item s10-highlight-concern">
            <span class="s10-highlight-label">Concern:</span>
            <span class="s10-highlight-text">{concern1}</span>
        </div>
        <div class="s10-highlight-item s10-highlight-concern">
            <span class="s10-highlight-label">Concern:</span>
            <span class="s10-highlight-text">{concern2}</span>
        </div>
    </div>
    """

    html = f"""
    <section class="s10-radar-section">
        <div class="s10-section-container">
            <h2 class="s10-section-title"></h2>
            <div class="s10-subtitle-row">
                <p class="s10-section-subtitle">More progression metrics for {all_metrics.get('team_name')}</p>
                <p class="s10-section-subtitle s10-section-subtitle-right">Progression Scatter Chart</p>
            </div>

            <div class="s10-radar-container">
                <div class="s10-radar-chart-wrapper">
                    {radar_svg}
                </div>
                <div class="s10-radar-chart-wrapper">
                    {scatter_svg}
                </div>
            </div>

            {highlights_html}
        </div>
    </section>
    """
    return html


def get_styles() -> str:
    """Return CSS styles for section 10."""
    return """
    <style>
    .s10-radar-section {
      padding: 40px 48px;
      background: white;
      border-top: 1px solid #e5e5e5;
      page-break-after: always;
    }

    .s10-section-container {
      max-width: 1000px;
    }

    .s10-section-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 24px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 4px;
    }

    .s10-subtitle-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .s10-section-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: #999;
      margin: 0;
    }

    .s10-section-subtitle-right {
      text-align: right;
    }

    .s10-radar-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      align-items: start;
    }

    .s10-radar-chart-wrapper {
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .s10-radar-chart {
      max-width: 100%;
      height: auto;
    }

    .s10-highlights-section {
      margin-top: 24px;
      padding-top: 16px;
      border-top: 1px solid #e5e5e5;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .s10-highlight-item {
      padding: 12px 16px;
      border-left: 4px solid #1a4fa3;
      border-radius: 4px;
      background: #f8fafc;
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      line-height: 1.2;
      color: #333;
    }

    .s10-highlight-label {
      font-weight: 600;
      color: #0f1923;
      margin-right: 6px;
    }

    .s10-highlight-text {
      color: #555;
      font-weight: 400;
    }

    .s10-highlight-strength {
      border-left-color: #27ae60;
      background: #f0fdf4;
    }

    .s10-highlight-strength .s10-highlight-label {
      color: #27ae60;
    }

    .s10-highlight-concern {
      border-left-color: #e74c3c;
      background: #fef2f2;
    }

    .s10-highlight-concern .s10-highlight-label {
      color: #e74c3c;
    }

    .s10-highlight-tactical {
      border-left-color: #f39c12;
      background: #fffbf0;
    }

    .s10-highlight-tactical .s10-highlight-label {
      color: #f39c12;
    }
    </style>
    """

