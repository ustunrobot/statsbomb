#!/usr/bin/env python3
"""Section 0: Key derived metrics overview."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.metrics import Metric

section_data = {}

# Derived metrics
section_data['Derived_Metrics'] = {
    # 'xg_per_game': Metric(value=1.82, value_pg=1.82, percentile=71.0, percentile_order=7, percentile_total=24, sample_size=5, average=1.82, z_score=0.7, label="xG Game"),
    # 'shot_volume': Metric(value=48, value_pg=9.6, percentile=68.0, percentile_order=8, percentile_total=24, sample_size=5, average=9.6, z_score=0.6, label="Shot Volume"),
    # 'shot_quality': Metric(value=0.26, value_pg=0.052, percentile=62.0, percentile_order=9, percentile_total=24, sample_size=5, average=0.052, z_score=0.4, label="Shot Quality", bar_label_low="", bar_label_high=""),
    # 'finishing': Metric(value=0.95, value_pg=0.19, percentile=58.0, percentile_order=10, percentile_total=24, sample_size=5, average=0.19, z_score=0.3, label="Finishing", bar_label_low="Bad", bar_label_high="Good"),
}


def render_derived_metrics_cards(metrics_dict: dict) -> str:
    """Render derived metrics with distinct colors for each metric.

    Args:
        metrics_dict: Dictionary of metrics to render
    """
    color_mapping = {
        'xg_for_total': 's0-metric-card-light-teal',
        'shot_for_total': 's0-metric-card-light-brick',
        'xgf_per_shot': 's0-metric-card-light-gray-custom',
        'goal_per_xgf': 's0-metric-card-light-lavender'
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

        # Use label2 as the main display name
        display_name = metric.label2 if metric.label2 else metric.label

        background_class = color_mapping.get(metric_name, "s0-metric-card")
        card_class = f"s0-metric-card {background_class}"

        # Format label and percentile separately for alignment
        label_text = metric.label if metric.label else ""
        percentile_text = f"P: ({metric.percentile_order}/{metric.percentile_total})" 

        cards_html += f"""
            <div class="{card_class}">
                <div class="s0-metric-card-name">{display_name}</div>
                <div class="s0-metric-card-value">{metric.value_pg:.2f}</div>
                <div class="s0-metric-card-zscore">
                    <span class="s0-metric-label-left">{label_text}</span>
                    <span class="s0-metric-percentile-right">{percentile_text}</span>
                </div>
                <div class="s0-metric-card-bar">
                    <div class="s0-metric-card-bar-background">
                        <div class="s0-metric-card-bar-center"></div>
                        <div class="s0-metric-card-bar-fill" style="left: {bar_left}%; width: {bar_width}%; background-color: {bar_color};"></div>
                    </div>
                </div>
                <div class="s0-metric-card-bar-labels">
                    <span class="s0-metric-card-bar-label-left">{metric.bar_label_low}</span>
                    <span class="s0-metric-card-bar-label-right">{metric.bar_label_high}</span>
                </div>
            </div>
        """
    return cards_html


def render_derived_metrics_section(all_metrics: dict) -> str:
    """Render section 0 with derived metrics overview."""

    metrics_to_display = {}

    # Extract metrics from the xg layer    
    metric_keys = [
        ('xg_for_total', 'xG per Game', 'Expected Goals', '', ''),
        ('shot_for_total', 'Shots per Game', 'Shot Volume', '', ''),
        ('xgf_per_shot', 'xGF per Shot', 'Shot Quality', '', ''),
        ('goal_per_xgf', 'Goals per xGF', 'Finishing', '', ''),
    ]

    for key, custom_label, label2, bar_label_low, bar_label_high in metric_keys:                
        metric = all_metrics.get(key, Metric.default())
        
        metric.label = custom_label        
        metric.label2 = label2
        metric.bar_label_low = bar_label_low
        metric.bar_label_high = bar_label_high
        metrics_to_display[key] = metric

    derived_metrics_html = render_derived_metrics_cards(metrics_to_display)

    html = f"""
    <section class="s0-derived-metrics-section">
        <div class="s0-section-container">
            <h2 class="s0-section-title">Attacking</h2>
            <p class="s0-section-subtitle">Chance creation metrics for {all_metrics.get('team_name')}</p>

            <div class="s0-derived-metrics-grid">
                {derived_metrics_html}
            </div>
        </div>
    </section>
    """
    return html


def get_styles() -> str:
    """Return CSS styles for section 0."""
    return """
    <style>
    .s0-derived-metrics-section {
      padding: 40px 48px;
      background: white;
      border-top: 1px solid #e5e5e5;
    }

    .s0-section-container {
      max-width: 1000px;
    }

    .s0-section-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 24px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 4px;
    }

    .s0-section-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: #999;
      margin-bottom: 24px;
    }

    .s0-derived-metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }

    .s0-metric-card {
      border: 1px solid #d9d9d9;
      border-radius: 6px;
      padding: 12px;
      background: white;
    }

    .s0-metric-card.s0-metric-card-light-teal {
      background: #ecfbfd;
      border: none;
    }

    .s0-metric-card.s0-metric-card-light-brick {
      background: #fdf2ed;
      border: none;
    }

    .s0-metric-card.s0-metric-card-light-gray-custom {
      background: #f5f7fa;
      border: none;
    }

    .s0-metric-card.s0-metric-card-light-lavender {
      background: #fef7ff;
      border: none;
    }

    .s0-metric-card-name {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 9px;
      color: #777777;
      font-weight: 500;
      margin-bottom: 6px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }

    .s0-metric-card-value {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 16px;
      font-weight: 700;
      color: #0f1923;
      margin-bottom: 6px;
    }

    .s0-metric-card-zscore {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 10px;
      color: #999;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .s0-metric-label-left {
      text-align: left;
      flex: 1;
    }

    .s0-metric-percentile-right {
      text-align: right;
      flex: 0 0 auto;
    }

    .s0-metric-card-bar {
      height: 18px;
      display: flex;
      align-items: center;
      position: relative;
    }

    .s0-metric-card-bar-background {
      width: 100%;
      height: 5px;
      background: #e5e5e5;
      border-radius: 3px;
      position: relative;
    }

    .s0-metric-card-bar-center {
      position: absolute;
      left: 50%;
      top: -3px;
      width: 1.5px;
      height: 11px;
      background: #999;
      transform: translateX(-50%);
    }

    .s0-metric-card-bar-fill {
      position: absolute;
      top: 0;
      height: 5px;
      border-radius: 3px;
      transition: all 0.3s ease;
    }

    .s0-metric-card-bar-labels {
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

    .s0-metric-card-bar-label-left {
      text-align: left;
    }

    .s0-metric-card-bar-label-right {
      text-align: right;
    }
    </style>
    """


if __name__ == "__main__":
    # Test the function
    html_output = render_derived_metrics_section(section_data)
    print(html_output)
