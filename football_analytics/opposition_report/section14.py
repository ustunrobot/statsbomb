#!/usr/bin/env python3
"""Section 14: Defensive and pressing metrics radar chart."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from event_based.metrics import Metric
from .charts import create_scatter_chart, create_radar_chart
from .insights_engine import InsightGenerator

section_data = {}

def get_metrics_to_display(all_metrics: dict, statsbomb_team_metrics: dict) -> dict:
    metrics_to_display = {}
    # Extract defensive and pressing metrics for radar chart
    metric_keys = [        
        ('xg_against_set_piece_total', 'xGA Set Piece', '', '', '', False, True),
        ('team_season_counterpressures_pg', 'Counterpress pG', '', '', '', False, False),
        ('team_season_counterpressure_regains_pg', 'Regains from CP pG', '', '', '', False, False),
        ('team_season_fhalf_pressures_ratio', 'F.Half Press Ratio', '', '', '', True, False),
        ('team_season_high_press_shots_conceded_pg', 'Shots Conceded from press', '', '', '', False, True),
        ('team_season_defensive_action_regains_pg', 'Regains pG', '', '', '', False, False),
    ]

    for key, custom_label, label2, bar_label_low, bar_label_high, is_percentage, is_reverse in metric_keys:
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
        metric.show_as_percentage = is_percentage
        metric.reverse = is_reverse
        metrics_to_display[key] = metric

    return metrics_to_display

def render_radar_section(all_metrics: dict, team_metrics: dict, statsbomb_team_metrics: dict, team_name: str, league_table: dict = None) -> str:
    """Render section 14 with defensive radar chart and scatter chart side-by-side."""
    # Extract specific team metrics from statsbomb_team_metrics (which now contains all teams)
    team_statsbomb_metrics = statsbomb_team_metrics.get(team_name, {})
    metrics = get_metrics_to_display(team_metrics, team_statsbomb_metrics)
    radar_svg = create_radar_chart(metrics)
    quadrant_labels =   {
                    'top_right': 'Aggressive-Efficient',
                    'bottom_right': 'Selective-Efficient',
                    'top_left': 'Aggressive-Inefficient',
                    'bottom_left': 'Passive-Inefficient'
                }
    scatter_svg = create_scatter_chart(all_metrics, statsbomb_team_metrics, team_name,
                                           x_metric_key='team_season_pressure_regains_pg',
                                           y_metric_key='team_season_pressures_pg',
                                           x_axis_label='Press Regains pG',
                                           y_axis_label='Pressures pG', quadrants=quadrant_labels,
                                           league_table=league_table)

    # Generate defensive insights from metrics
    generator = InsightGenerator(team_metrics, league_table, team_name, statsbomb_team_metrics)
    defense_insights = generator.generate_defense_insights()

    # Defensive profile highlights with fallback defaults
    default_insights = [
        "Defensive solidity being evaluated",
        "Set piece vulnerability assessment pending",
        "Aerial dominance metrics under review",
        "Counter-pressing efficiency to be analyzed"
    ]

    # Use generated insights if available, otherwise use defaults
    while len(defense_insights) < 4:
        defense_insights.append(default_insights[len(defense_insights)])

    strength1 = defense_insights[0]
    strength2 = defense_insights[1]
    concern1 = defense_insights[2]
    concern2 = defense_insights[3]    

    # Defensive profile highlights
    highlights_html = f"""
    <div class="s14-highlights-section">
        <div class="s14-highlight-item s14-highlight-strength">
            <span class="s14-highlight-label">Strength:</span>
            <span class="s14-highlight-text">{strength1}</span>
        </div>
        <div class="s14-highlight-item s14-highlight-strength">
            <span class="s14-highlight-label">Strength:</span>
            <span class="s14-highlight-text">{strength2}</span>
        </div>
        <div class="s14-highlight-item s14-highlight-concern">
            <span class="s14-highlight-label">Concern:</span>
            <span class="s14-highlight-text">{concern1}</span>
        </div>
        <div class="s14-highlight-item s14-highlight-concern">
            <span class="s14-highlight-label">Concern:</span>
            <span class="s14-highlight-text">{concern2}</span>
        </div>
    </div>
    """

    html = f"""
    <section class="s14-radar-section">
        <div class="s14-section-container">
            <h2 class="s14-section-title"></h2>
            <div class="s14-subtitle-row">
                <p class="s14-section-subtitle">Defensive and pressing metrics for {all_metrics.get('team_name')}</p>
                <p class="s14-section-subtitle s14-section-subtitle-right">Pressure Regains vs Pressures</p>
            </div>

            <div class="s14-radar-container">
                <div class="s14-radar-chart-wrapper">
                    {radar_svg}
                </div>
                <div class="s14-radar-chart-wrapper">
                    {scatter_svg}
                </div>
            </div>

            {highlights_html}
        </div>
    </section>
    """
    return html


def get_styles() -> str:
    """Return CSS styles for section 14."""
    return """
    <style>
    .s14-radar-section {
      padding: 40px 48px;
      background: white;
      border-top: 1px solid #e5e5e5;
      page-break-after: always;
    }

    .s14-section-container {
      max-width: 1000px;
    }

    .s14-section-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 24px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 4px;
    }

    .s14-subtitle-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .s14-section-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: #999;
      margin: 0;
    }

    .s14-section-subtitle-right {
      text-align: right;
    }

    .s14-radar-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      align-items: start;
    }

    .s14-radar-chart-wrapper {
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .s14-radar-chart {
      max-width: 100%;
      height: auto;
    }

    .s14-highlights-section {
      margin-top: 24px;
      padding-top: 16px;
      border-top: 1px solid #e5e5e5;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .s14-highlight-item {
      padding: 12px 16px;
      border-left: 4px solid #1a4fa3;
      border-radius: 4px;
      background: #f8fafc;
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      line-height: 1.5;
      color: #333;
    }

    .s14-highlight-label {
      font-weight: 600;
      color: #0f1923;
      margin-right: 6px;
    }

    .s14-highlight-text {
      color: #555;
      font-weight: 400;
    }

    .s14-highlight-strength {
      border-left-color: #27ae60;
      background: #f0fdf4;
    }

    .s14-highlight-strength .s14-highlight-label {
      color: #27ae60;
    }

    .s14-highlight-concern {
      border-left-color: #e74c3c;
      background: #fef2f2;
    }

    .s14-highlight-concern .s14-highlight-label {
      color: #e74c3c;
    }

    .s14-highlight-tactical {
      border-left-color: #f39c12;
      background: #fffbf0;
    }

    .s14-highlight-tactical .s14-highlight-label {
      color: #f39c12;
    }
    </style>
    """


if __name__ == "__main__":
    # Test the function
    html_output = render_radar_section(section_data, {}, {}, "Test Team")
    print(html_output)
