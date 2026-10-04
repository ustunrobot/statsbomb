#!/usr/bin/env python3
"""Section 17: SkillCorner physical data overview."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from event_based.metrics import Metric
from .charts import create_radar_chart, render_metric_cards

section_data = {}


def get_card_metrics_to_display(team_metrics_all: dict) -> dict:
    """Extract the summary physical metrics for the metric cards (all from physical_all)."""
    metrics_to_display = {}

    metric_keys = [
        ('total_metersperminute_full_all_p90', 'meters/min', 'Running Volume'),
        ('hi_distance_full_all_p90', 'meters', 'HI Running Distance'),
        ('peak_velocity_top3', 'km/h', 'Peak Velocity Top3'),
        ('sprint_distance_full_all_p90', 'meters', 'Sprint Distance'),
    ]

    for key, custom_label, label2 in metric_keys:
        metric = team_metrics_all.get(key, Metric.default())
        metric.label = custom_label
        metric.label2 = label2
        metrics_to_display[key] = metric

    return metrics_to_display


def get_radar_metrics_to_display(team_metrics_otip: dict, team_metrics_tip: dict, team_metrics_all: dict) -> dict:
    """Extract the physical metrics for the radar chart, drawn from the otip/tip/all sources."""
    metrics_to_display = {}

    metric_keys = [
        ('total_metersperminute_full_otip', team_metrics_otip, 'meters/min', 'Out of Possession Running'),
        ('total_metersperminute_full_tip', team_metrics_tip, 'meters/min', 'In Possession Running'),
        ('hi_distance_full_otip', team_metrics_otip, 'meters', 'Out of Possession HI Distance'),
        ('hi_distance_full_tip', team_metrics_tip, 'meters', 'In Possession HI Distance'),
        ('cod_count_full_all_p90', team_metrics_all, '', '#Change of Direction'),
        ('sprint_count_full_all_p90', team_metrics_all, '', 'Sprint Count'),
    ]

    for key, source_metrics, custom_label, label2 in metric_keys:
        metric = source_metrics.get(key, Metric.default())
        metric.label = custom_label
        metric.label2 = label2
        metrics_to_display[key] = metric

    return metrics_to_display


def render_physical_data_section(skillcorner_team_metrics: dict, team_name: str) -> str:
    """Render section 17 with SkillCorner physical data: summary cards and a radar chart."""
    skillcorner_team_metrics = skillcorner_team_metrics or {}
    team_metrics_all = skillcorner_team_metrics.get('physical_all', {}).get(team_name, {})
    team_metrics_otip = skillcorner_team_metrics.get('physical_otip', {}).get(team_name, {})
    team_metrics_tip = skillcorner_team_metrics.get('physical_tip', {}).get(team_name, {})

    card_metrics = get_card_metrics_to_display(team_metrics_all)
    cards_html = render_metric_cards(card_metrics)

    radar_metrics = get_radar_metrics_to_display(team_metrics_otip, team_metrics_tip, team_metrics_all)
    radar_svg = create_radar_chart(radar_metrics)

    html = f"""
    <section class="s17-physical-section">
        <div class="s17-section-container">
            <h2 class="s17-section-title">Physical Data</h2>            
            <p class="s17-section-subtitle">SkillCorner physical metrics for {team_name}</p>
            <div class="s17-metrics-grid">
                {cards_html}
            </div>

            <div class="s17-radar-chart-wrapper">
                {radar_svg}
            </div>
        </div>
    </section>
    """
    return html


def get_styles() -> str:
    """Return CSS styles for section 17."""
    return """
    <style>
    .s17-physical-section {
      padding: 40px 48px;
      background: white;
      border-top: 1px solid #e5e5e5;
      page-break-after: always;
    }

    .s17-section-container {
      max-width: 1000px;
    }

    .s17-section-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 24px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 4px;
    }

    .s17-section-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: #999;
      margin-bottom: 24px;
    }

    .s17-metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 32px;
    }

    .s17-radar-chart-wrapper {
      display: flex;
      justify-content: center;
      align-items: center;
    }
    </style>
    """


if __name__ == "__main__":
    # Test the function
    html_output = render_physical_data_section({}, "Test Team")
    print(html_output)
