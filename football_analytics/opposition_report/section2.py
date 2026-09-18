#!/usr/bin/env python3
"""Section 2: Team metrics overview."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.metrics import Metric

section_data = {}

def render_metrics_section(section_data: dict) -> str:
    """Render the team metrics overview section with card layout."""
    metrics = section_data.get('Metrics', {})

    cards_html = ""
    for metric_name, metric in metrics.items():
        z_score = metric.z_score
        # Map z-score from -2 to +2 range to 0-100% position
        # Formula: ((z_score + 2) / 4) * 100
        bar_end_position = ((z_score + 2) / 4) * 100
        bar_end_position = max(0, min(100, bar_end_position))  # Clamp to 0-100

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

        cards_html += f"""
            <div class="metric-card">
                <div class="metric-card-name">{metric_name.upper()}</div>
                <div class="metric-card-value">{metric.value:.1f}</div>
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
    <section class="metrics-section">
        <div class="section-container">
            <h2 class="section-title">Key Metrics</h2>
            <p class="section-subtitle">Aggregate performance for {section_data.get('Team', 'Team')}</p>

            <div class="metrics-grid">
                {cards_html}
            </div>
        </div>
    </section>
    """
    return html


def get_styles() -> str:
    """Return CSS styles for section 2."""
    return """
    <style>
    .metrics-section {
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

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
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
      height: 6px;
      background: #e5e5e5;
      border-radius: 3px;
      position: relative;
    }

    .metric-card-bar-center {
      position: absolute;
      left: 50%;
      top: -4px;
      width: 2px;
      height: 14px;
      background: #999;
      transform: translateX(-50%);
    }

    .metric-card-bar-fill {
      position: absolute;
      top: 0;
      height: 6px;
      border-radius: 3px;
      transition: all 0.3s ease;
    }
    </style>
    """


if __name__ == "__main__":
    # Test the function
    html_output = render_metrics_section(section_data)
    print(html_output)
