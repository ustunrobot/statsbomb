#!/usr/bin/env python3
"""Section 9: Key derived metrics overview."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from event_based.metrics import Metric
from .charts import render_metric_cards

section_data = {}

# Derived metrics
section_data['Derived_Metrics'] = {
    # 'xg_per_game': Metric(value=1.82, value_pg=1.82, percentile=71.0, percentile_order=7, percentile_total=24, sample_size=5, average=1.82, z_score=0.7, label="xG Game"),
    # 'shot_volume': Metric(value=48, value_pg=9.6, percentile=68.0, percentile_order=8, percentile_total=24, sample_size=5, average=9.6, z_score=0.6, label="Shot Volume"),
    # 'shot_quality': Metric(value=0.26, value_pg=0.052, percentile=62.0, percentile_order=9, percentile_total=24, sample_size=5, average=0.052, z_score=0.4, label="Shot Quality", bar_label_low="", bar_label_high=""),
    # 'finishing': Metric(value=0.95, value_pg=0.19, percentile=58.0, percentile_order=10, percentile_total=24, sample_size=5, average=0.19, z_score=0.3, label="Finishing", bar_label_low="Bad", bar_label_high="Good"),
}


def render_derived_metrics_section(all_metrics: dict, statsbomb_metrics: dict, team_name: str) -> str:
    """Render section 9 with derived metrics overview."""

    # Extract specific team metrics from statsbomb_metrics (which now contains all teams)
    team_statsbomb_metrics = statsbomb_metrics.get(team_name, {})

    metrics_to_display = {}

    # Extract metrics from the xg layer
    metric_keys = [
        ('team_season_possession', 'Possession', '', '', ''),
        ('team_season_gk_long_pass_ratio', 'GK Long ball', '', '', ''),
        ('team_season_directness', 'Directness', '', '', ''),
        ('team_season_passing_ratio', 'Pass Completion', '', '', ''),
        #('team_season_box_cross_ratio', 'box crosses / box passes', 'Box Cross %', '', ''),
    ]

    for key, custom_label, label2, bar_label_low, bar_label_high in metric_keys:
        if key in all_metrics:
          metric = all_metrics.get(key, Metric.default())
        else:
          metric = team_statsbomb_metrics.get(key, Metric.default())

        metric.label = custom_label
        metric.label2 = label2
        metric.bar_label_low = bar_label_low
        metric.bar_label_high = bar_label_high
        metric.show_as_percentage = True
        metrics_to_display[key] = metric

    derived_metrics_html = render_metric_cards(metrics_to_display)

    html = f"""
    <section class="s9-derived-metrics-section">
        <div class="s9-section-container">
            <h2 class="s9-section-title">Possession</h2>
            <p class="s9-section-subtitle">Possession and Progression metrics for {team_name}</p>

            <div class="s9-derived-metrics-grid">
                {derived_metrics_html}
            </div>
        </div>
    </section>
    """
    return html


def get_styles() -> str:
    """Return CSS styles for section 9."""
    return """
    <style>
    .s9-derived-metrics-section {
      padding: 40px 48px;
      background: white;
      border-top: 1px solid #e5e5e5;
      page-break-after: always;
    }

    .s9-section-container {
      max-width: 1000px;
    }

    .s9-section-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 24px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 4px;
    }

    .s9-section-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: #999;
      margin-bottom: 24px;
    }

    .s9-derived-metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }
    </style>
    """


if __name__ == "__main__":
    # Test the function
    html_output = render_derived_metrics_section(section_data)
    print(html_output)
