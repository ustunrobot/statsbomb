#!/usr/bin/env python3
"""Section 13: Defending derived metrics overview."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from event_based.metrics import Metric
from .charts import render_metric_cards

section_data = {}

# Derived metrics
section_data['Defending_Metrics'] = {
}


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

    defending_metrics_html = render_metric_cards(metrics_to_display)

    
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
    </style>
    """


if __name__ == "__main__":
    # Test the function
    html_output = render_defending_section(section_data)
    print(html_output)
