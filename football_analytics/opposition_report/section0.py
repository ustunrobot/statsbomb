#!/usr/bin/env python3
"""Section 0: Key derived metrics overview."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from event_based.metrics import Metric
from .charts import render_metric_cards

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

    derived_metrics_html = render_metric_cards(metrics_to_display)

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
    </style>
    """


