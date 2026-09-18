#!/usr/bin/env python3
"""Section 3: Team metrics radar chart."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.metrics import Metric
from football_analytics.opposition_report.charts import create_scatter_chart, create_radar_chart
from football_analytics.opposition_report.insights_engine import InsightGenerator

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

def render_radar_section(all_metrics: dict, team_metrics: dict, statsbomb_team_metrics: dict, team_name: str, league_table: dict = None) -> str:
    """Render section 3 with radar chart and scatter chart side-by-side."""
    # Extract specific team metrics from statsbomb_team_metrics (which now contains all teams)
    team_statsbomb_metrics = statsbomb_team_metrics.get(team_name, {})
    metrics = get_metrics_to_display(team_metrics, team_statsbomb_metrics)
    radar_svg = create_radar_chart(metrics)
    scatter_svg = create_scatter_chart(all_metrics, statsbomb_team_metrics, team_name,
                                           x_metric_key='xg_for_total',
                                           y_metric_key='xg_against_total',
                                           x_axis_label='xGF',
                                           y_axis_label='xGA',
                                           league_table=league_table)

    # Generate attacking insights from metrics
    team_statsbomb_metrics_full = statsbomb_team_metrics.get(team_name, {})
    generator = InsightGenerator(team_metrics, league_table, team_name, statsbomb_team_metrics)
    attacking_insights = generator.generate_attacking_insights()

    # Attacking profile highlights with fallback defaults
    default_insights = [
        "Attacking performance requires further analysis",
        "Offensive efficiency metrics pending",
        "Defensive robustness under review",
        "Set piece execution to be evaluated"
    ]

    # Use generated insights if available, otherwise use defaults
    while len(attacking_insights) < 4:
        attacking_insights.append(default_insights[len(attacking_insights)])

    strength1 = attacking_insights[0]
    strength2 = attacking_insights[1]
    concern1 = attacking_insights[2]
    concern2 = attacking_insights[3]

    highlights_html = f"""
    <div class="s3-highlights-section">
        <div class="s3-highlight-item s3-highlight-strength">
            <span class="s3-highlight-label">Strength:</span>
            <span class="s3-highlight-text">{strength1}</span>
        </div>
        <div class="s3-highlight-item s3-highlight-strength">
            <span class="s3-highlight-label">Strength:</span>
            <span class="s3-highlight-text">{strength2}</span>
        </div>
        <div class="s3-highlight-item s3-highlight-concern">
            <span class="s3-highlight-label">Concern:</span>
            <span class="s3-highlight-text">{concern1}</span>
        </div>
        <div class="s3-highlight-item s3-highlight-concern">
            <span class="s3-highlight-label">Concern:</span>
            <span class="s3-highlight-text">{concern2}</span>
        </div>
    </div>
    """

    html = f"""
    <section class="s3-radar-section">
        <div class="s3-section-container">
            <h2 class="s3-section-title"></h2>
            <div class="s3-subtitle-row">
                <p class="s3-section-subtitle">More attacking metrics for {all_metrics.get('team_name')}</p>
                <p class="s3-section-subtitle s3-section-subtitle-right">xG Scatter Chart</p>
            </div>

            <div class="s3-radar-container">
                <div class="s3-radar-chart-wrapper">
                    {radar_svg}
                </div>
                <div class="s3-radar-chart-wrapper">
                    {scatter_svg}
                </div>
            </div>

            {highlights_html}
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

    .s3-subtitle-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .s3-section-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: #999;
      margin: 0;
    }

    .s3-section-subtitle-right {
      text-align: right;
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

    .s3-highlights-section {
      margin-top: 24px;
      padding-top: 16px;
      border-top: 1px solid #e5e5e5;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .s3-highlight-item {
      padding: 12px 16px;
      border-left: 4px solid #1a4fa3;
      border-radius: 4px;
      background: #f8fafc;
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      line-height: 1.0;
      color: #333;
    }

    .s3-highlight-label {
      font-weight: 600;
      color: #0f1923;
      margin-right: 6px;
    }

    .s3-highlight-text {
      color: #555;
      font-weight: 400;
    }

    .s3-highlight-strength {
      border-left-color: #27ae60;
      background: #f0fdf4;
    }

    .s3-highlight-strength .s3-highlight-label {
      color: #27ae60;
    }

    .s3-highlight-concern {
      border-left-color: #e74c3c;
      background: #fef2f2;
    }

    .s3-highlight-concern .s3-highlight-label {
      color: #e74c3c;
    }

    .s3-highlight-tactical {
      border-left-color: #f39c12;
      background: #fffbf0;
    }

    .s3-highlight-tactical .s3-highlight-label {
      color: #f39c12;
    }
    </style>
    """

