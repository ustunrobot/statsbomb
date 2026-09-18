#!/usr/bin/env python3
"""Section 13: Defending derived metrics overview."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.metrics import Metric
from football_analytics.opposition_report.charts import reverse_metric_if_needed

section_data = {}

# Derived metrics
section_data['Defending_Metrics'] = {
}


def render_defending_metrics_cards(metrics_dict: dict) -> str:
    """Render defending metrics with distinct colors for each metric.

    Args:
        metrics_dict: Dictionary of metrics to render
    """
    color_mapping = {
        'xg_against_total': 's13-metric-card-light-amber',
        'team_season_defensive_distance': 's13-metric-card-light-rose',
        'team_season_ppda': 's13-metric-card-light-indigo',
        'team_season_aggression': 's13-metric-card-light-emerald'
    }
    
    cards_html = ""
    for metric_name, metric in metrics_dict.items():
        metric = reverse_metric_if_needed(metric)  # Reverse metrics if needed
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

        # Use label2 as the main display name
        display_name = metric.label2 if metric.label2 else metric.label

        background_class = color_mapping.get(metric_name, "s13-metric-card")
        card_class = f"s13-metric-card {background_class}"

        # Format label and percentile separately for alignment
        label_text = metric.label if metric.label else ""
        percentile_text = f"P: {metric.percentile_order}/{metric.percentile_total}" 

        cards_html += f"""
            <div class="{card_class}">
                <div class="s13-metric-card-name">{display_name}</div>
                <div class="s13-metric-card-value">{metric.value_pg:.2f}</div>
                <div class="s13-metric-card-zscore">
                    <span class="s13-metric-label-left">{label_text}</span>
                    <span class="s13-metric-percentile-right">{percentile_text}</span>
                </div>
                <div class="s13-metric-card-bar">
                    <div class="s13-metric-card-bar-background">
                        <div class="s13-metric-card-bar-center"></div>
                        <div class="s13-metric-card-bar-fill" style="left: {bar_left}%; width: {bar_width}%; background-color: {bar_color};"></div>
                    </div>
                </div>
                <div class="s13-metric-card-bar-labels">
                    <span class="s13-metric-card-bar-label-left">{metric.bar_label_low}</span>
                    <span class="s13-metric-card-bar-label-right">{metric.bar_label_high}</span>
                </div>
            </div>
        """
    return cards_html


def render_defending_section(all_metrics: dict, statsbomb_team_metrics: dict) -> str:
    """Render section 13 with defending metrics overview."""

    metrics_to_display = {}

    # Extract metrics from the defensive layer
    metric_keys = [
        ('xg_against_total', 'xGA pG', 'xG Conceeded', '', '', True),
        ('team_season_defensive_distance', 'Defensive Distance', '', '', '', False),
        ('team_season_ppda', 'PPDA per Game', 'PPDA', '', '', True),
        ('team_season_aggression', 'Aggression', '', '', '', False),
    ]

    team_name = all_metrics.get('team_name', 'Team')
    team_statsbomb_metrics = statsbomb_team_metrics.get(team_name, {})


    for key, custom_label, label2, bar_label_low, bar_label_high, is_reverse in metric_keys:        

        if key in all_metrics:
            metric = all_metrics.get(key, Metric.default())
        else:
            metric = team_statsbomb_metrics.get(key, Metric.default())

        metric.label = custom_label
        metric.label2 = label2
        metric.bar_label_low = bar_label_low
        metric.bar_label_high = bar_label_high
        metric.reverse = is_reverse
        metrics_to_display[key] = metric

    defending_metrics_html = render_defending_metrics_cards(metrics_to_display)

    
    html = f"""
    <section class="s13-defending-metrics-section">
        <div class="s13-section-container">
            <h2 class="s13-section-title">Defending</h2>
            <p class="s13-section-subtitle">Defensive actions and pressure metrics for {team_name}</p>

            <div class="s13-defending-metrics-grid">
                {defending_metrics_html}
            </div>
        </div>
    </section>
    """
    return html


def get_styles() -> str:
    """Return CSS styles for section 13."""
    return """
    <style>
    .s13-defending-metrics-section {
      padding: 40px 48px;
      background: white;
      border-top: 1px solid #e5e5e5;
    }

    .s13-section-container {
      max-width: 1000px;
    }

    .s13-section-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 24px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 4px;
    }

    .s13-section-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: #999;
      margin-bottom: 24px;
    }

    .s13-defending-metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }

    .s13-metric-card {
      border: 1px solid #d9d9d9;
      border-radius: 6px;
      padding: 12px;
      background: white;
    }

    .s13-metric-card.s13-metric-card-light-amber {
      background: #fffbf0;
      border: none;
    }

    .s13-metric-card.s13-metric-card-light-rose {
      background: #ffe5f0;
      border: none;
    }

    .s13-metric-card.s13-metric-card-light-indigo {
      background: #f0e5ff;
      border: none;
    }

    .s13-metric-card.s13-metric-card-light-emerald {
      background: #e5fff0;
      border: none;
    }

    .s13-metric-card-name {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 9px;
      color: #777777;
      font-weight: 500;
      margin-bottom: 6px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }

    .s13-metric-card-value {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 16px;
      font-weight: 700;
      color: #0f1923;
      margin-bottom: 6px;
    }

    .s13-metric-card-zscore {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 10px;
      color: #999;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .s13-metric-label-left {
      text-align: left;
      flex: 1;
    }

    .s13-metric-percentile-right {
      text-align: right;
      flex: 0 0 auto;
    }

    .s13-metric-card-bar {
      height: 18px;
      display: flex;
      align-items: center;
      position: relative;
    }

    .s13-metric-card-bar-background {
      width: 100%;
      height: 5px;
      background: #e5e5e5;
      border-radius: 3px;
      position: relative;
    }

    .s13-metric-card-bar-center {
      position: absolute;
      left: 50%;
      top: -3px;
      width: 1.5px;
      height: 11px;
      background: #999;
      transform: translateX(-50%);
    }

    .s13-metric-card-bar-fill {
      position: absolute;
      top: 0;
      height: 5px;
      border-radius: 3px;
      transition: all 0.3s ease;
    }

    .s13-metric-card-bar-labels {
      display: flex;
      justify-content: space-between;
      margin-top: 4px;
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 8px;
      color: #999;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 500;
    }

    .s13-metric-card-bar-label-left {
      text-align: left;
    }

    .s13-metric-card-bar-label-right {
      text-align: right;
    }
    </style>
    """


if __name__ == "__main__":
    # Test the function
    html_output = render_defending_section(section_data)
    print(html_output)
