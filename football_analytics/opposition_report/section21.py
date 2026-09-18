#!/usr/bin/env python3
"""Section 21: Player metrics radar chart."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.metrics import Metric
from football_analytics.opposition_report.charts import create_radar_chart, render_metric_cards

def get_player_attacking_metrics_to_display(player_stats: dict) -> dict:
    """Extract attacking profile metrics for radar chart display."""
    metrics_to_display = {}

    metric_keys = [
        ('player_season_np_xg_90', 'np xG 90', 'Non-Penalty xG', '', '', False, False),
        ('player_season_npxgxa_90', 'xG+xA 90', 'Shooting & Creation', '', '', False, False),
        ('player_season_np_xg_per_shot', 'xG+xA 90', 'Shot Quality', '', '', True, False),
        ('player_season_op_key_passes_90', 'Key Passes 90', 'Chance Creation', '', '', False, False),
        ('player_season_dribbles_90', 'Dribbles 90', 'Successful Dribbles', '', '', False, False),
        ('player_season_touches_inside_box_90', 'Box Touches 90', 'Box Presence', '', '', False, False),
        ('player_season_shot_on_target_ratio', 'Shot Target %', 'Execution Quality', '', '', True, False),
        ('player_season_deep_progressions_90', 'Deep Prog 90', 'Final Third Entries', '', '', False, False),
        ('player_season_op_passes_into_box_90', 'Passes Box 90', 'Delivery into Danger', '', '', False, False),
        
    ]

    for key, custom_label, label2, bar_label_low, bar_label_high, perc, rev in metric_keys:
        # Try to get metric from player_stats
        if key in player_stats and isinstance(player_stats[key], Metric):
            metric = player_stats[key]
        else:
            metric = Metric.default()

        metric.show_as_percentage = perc
        metric.reverse = rev
        metric.label = custom_label
        metric.label2 = label2
        metric.bar_label_low = bar_label_low
        metric.bar_label_high = bar_label_high
        metrics_to_display[key] = metric

    return metrics_to_display


def get_player_possession_metrics_to_display(player_stats: dict) -> dict:
    """Extract possession profile metrics for radar chart display."""
    metrics_to_display = {}

    metric_keys = [
        ('player_season_passing_ratio', 'Pass Comp %', 'Pass Success %', '', '', True, False),
        ('player_season_obv_pass_90', 'Pass Comp %', 'Pass OBV /90', '', '', False, False),
        ('player_season_through_balls_90', 'Pass Comp %', 'Through Balls /90', '', '', True, False),
        ('player_season_lbp_completed_90', 'Line-Breaking /90', 'Line-Breaking Passes', '', '', False, False),
        ('player_season_carry_ratio', 'Carry Success %', 'Carry Success %', '', '', True, False),
        ('player_season_forward_pass_proportion', 'Forward Pass %', 'Intent to Progress', '', '', True, False),
        ('player_season_change_in_passing_ratio', 'Pressure Resilience', 'Under Press Resilience', '', '',False, False),
        ('player_season_deep_progressions_90', 'Deep Prog 90', 'Deep Progressions', '', '',False, False),
        ('player_season_turnovers_90', 'Turnovers 90', 'Turnovers /90', '', '',False, True),        
    ]

    for key, custom_label, label2, bar_label_low, bar_label_high, perc, rev in metric_keys:
        # Try to get metric from player_stats
        if key in player_stats and isinstance(player_stats[key], Metric):
            metric = player_stats[key]
        else:
            metric = Metric.default()

        metric.label = custom_label
        metric.label2 = label2
        metric.bar_label_low = bar_label_low
        metric.bar_label_high = bar_label_high
        metric.reverse = rev
        metric.show_as_percentage = perc

        # Reverse turnovers metric (lower is better, so invert percentile)
        if key == 'player_season_turnovers_90':
            if metric.percentile is not None:
                metric.percentile = 100 - metric.percentile

        metrics_to_display[key] = metric

    return metrics_to_display

def get_player_defending_metrics_to_display(player_stats: dict) -> dict:
    """Extract defending profile metrics for radar chart display."""
    metrics_to_display = {}

    metric_keys = [
        ('player_season_padj_tackles_90', 'Padj Tackles 90', 'P-Adj Tackles', '', '', False, False),
        ('player_season_padj_interceptions_90', 'Padj Interceptions 90', 'P-Adj Interceptions', '', '', False, False),
        ('player_season_aerial_wins_90', 'Aerial Wins 90', 'Aerial Dominance', '', '', False, False),
        ('player_season_dribble_faced_ratio', 'Dribble Stopped %', 'Stopped Dribbles %', '', '', True, False),
        ('player_season_clearance_90', 'Clearances 90', 'Defensive Interventions', '', '', False, False),
        ('player_season_pressure_regains_90', 'Pressure Regains 90', 'Pressing Quality', '', '', False, False),
        ('player_season_defensive_actions_above_expectation_90', 'Def Actions xE 90', 'Defence Responsibility', '', '', False, False),
    ]

    for key, custom_label, label2, bar_label_low, bar_label_high, perc, rev in metric_keys:
        # Try to get metric from player_stats
        if key in player_stats and isinstance(player_stats[key], Metric):
            metric = player_stats[key]
        else:
            metric = Metric.default()

        metric.label = custom_label
        metric.label2 = label2
        metric.bar_label_low = bar_label_low
        metric.bar_label_high = bar_label_high
        metric.reverse = rev
        metric.show_as_percentage = perc

        metrics_to_display[key] = metric

    return metrics_to_display

def get_player_summary_metrics_to_display(player_stats: dict) -> dict:
    """Extract summary metrics for display below radar charts."""
    metrics_to_display = {}

    metric_keys = [
        ('player_season_long_balls_90', 'Long ball attempts per 90', 'Long Balls', '', '', False, False),
        ('player_season_pass_into_pressure_ratio', 'Ratio of passes into pressure', 'Passes into Pressure', '', '', True, False),
        ('player_season_obv_90', 'On Ball Value added per 90', 'OBV /90', '', '', False, False),
        ('player_season_pass_length', 'Average Pass Length', 'Pass Length', '', '', False, False),
        ('player_season_xgchain_90', 'Share in xG chain per 90', 'xG Chain 90', '', '', False, False),
    ]

    for key, custom_label, label2, bar_label_low, bar_label_high, perc, rev in metric_keys:
        # Try to get metric from player_stats
        if key in player_stats and isinstance(player_stats[key], Metric):
            metric = player_stats[key]
        else:
            metric = Metric.default()

        metric.label = custom_label
        metric.label2 = label2
        metric.bar_label_low = bar_label_low
        metric.bar_label_high = bar_label_high
        metric.reverse = rev
        metric.show_as_percentage = perc

        metrics_to_display[key] = metric

    return metrics_to_display

def render_minutes_info(player_stats: dict) -> str:
    """Render minutes played info with warning if below threshold as a single line."""
    minutes_played = player_stats.get('player_season_minutes')
    minutes_threshold = player_stats.get('minutes_threshold')

    if minutes_played is None:
        return ""

    # Extract numeric value if it's a Metric object
    if isinstance(minutes_played, Metric):
        minutes_value = minutes_played.value or 0
    else:
        minutes_value = float(minutes_played) if minutes_played else 0

    minutes_int = int(minutes_value)

    # Check if minutes are below threshold
    is_below_threshold = False
    if minutes_threshold is not None:
        threshold_int = int(minutes_threshold)
        is_below_threshold = minutes_int < threshold_int

    # Build the message
    if is_below_threshold:
        threshold_int = int(minutes_threshold)
        message = f"⚠️ Minutes played: <span class=\"s21-minutes-value\">{minutes_int}</span> minutes (below threshold of {threshold_int} min - reliability may be affected)"
        subtitle_class = "s21-section-subtitle s21-minutes-warning-text"
    else:
        message = f"Minutes played: <span class=\"s21-minutes-value\">{minutes_int}</span> minutes"
        subtitle_class = "s21-section-subtitle"

    html = f"""
    <div class="s21-subtitle-row">
        <p class="{subtitle_class}">{message}</p>
    </div>
    """
    return html

def render_player_radar_section(player_stats: dict) -> str:
    """Render player radar chart sections for attacking, possession, and defending profiles."""
    player_name = player_stats.get('player_name', 'Unknown Player')

    # Attacking profile
    attacking_metrics = get_player_attacking_metrics_to_display(player_stats)
    attacking_radar_svg = create_radar_chart(attacking_metrics, default_size=320)

    # Possession profile
    possession_metrics = get_player_possession_metrics_to_display(player_stats)
    possession_radar_svg = create_radar_chart(possession_metrics, default_size=320)

    # Defending profile
    defending_metrics = get_player_defending_metrics_to_display(player_stats)
    defending_radar_svg = create_radar_chart(defending_metrics, default_size=320)

    # Summary metrics for cards
    summary_metrics = get_player_summary_metrics_to_display(player_stats)
    summary_cards_html = render_metric_cards(summary_metrics)

    # Minutes played info
    minutes_info_html = render_minutes_info(player_stats)

    html = f"""
    <section class="s21-radar-section">
        <div class="s21-section-container">
            <h2 class="s21-section-title"></h2>
            <div class="s21-subtitle-row">
                <p class="s21-section-subtitle">Summary of attacking, possession and defending profiles</p>
            </div>

            <div class="s21-radar-container">
                <div class="s21-chart-column">
                    <p class="s21-chart-title">Attacking</p>
                    <div class="s21-radar-chart-wrapper">
                        {attacking_radar_svg}
                    </div>
                </div>
                <div class="s21-chart-column">
                    <p class="s21-chart-title">Possession</p>
                    <div class="s21-radar-chart-wrapper">
                        {possession_radar_svg}
                    </div>
                </div>
                <div class="s21-chart-column">
                    <p class="s21-chart-title">Defending</p>
                    <div class="s21-radar-chart-wrapper">
                        {defending_radar_svg}
                    </div>
                </div>
            </div>

            <div class="s21-subtitle-row">
                <p class="s21-section-subtitle">Additional metrics for the player</p>
            </div>
            <div class="s21-summary-metrics">
                {summary_cards_html}
            </div>

            {minutes_info_html}
        </div>
    </section>
    """
    return html


def get_styles() -> str:
    """Return CSS styles for section 21 optimized for A4 landscape."""
    return """
    <style>
    .s21-radar-section {
      padding: 24px 48px;
      background: white;
      border-top: 1px solid #e5e5e5;
      page-break-after: always;
    }

    .s21-section-container {
      max-width: 100%;
    }

    .s21-section-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 20px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 4px;
    }

    .s21-subtitle-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }

    .s21-section-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 12px;
      color: #999;
      margin: 0;
    }

    .s21-radar-container {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 16px;
    }

    .s21-chart-column {
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .s21-chart-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 12px;
      font-weight: 600;
      color: var(--ink);
      margin: 0 0 12px 0;
      text-align: center;
    }

    .s21-radar-chart-wrapper {
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .s21-radar-chart {
      max-width: 100%;
      height: auto;
    }

    .s21-metrics-summary {
      padding: 12px;
      background: #f8fafc;
      border-radius: 4px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      border-left: 4px solid #1a4fa3;
    }

    .s21-summary-item {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .s21-summary-label {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 10px;
      font-weight: 500;
      color: #999;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .s21-summary-value {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      font-weight: 600;
      color: var(--ink);
    }

    .s21-summary-metrics {
      margin-top: 24px;
      margin-bottom: 24px;
      padding-top: 16px;
      border-top: 1px solid #e5e5e5;
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }

    .metric-card {
      flex: 0 1 calc(20% - 10px);
      padding: 12px;
      background: #f8fafc;
      border-left: 4px solid #1a4fa3;
      border-radius: 4px;
      font-family: 'Inter', system-ui, sans-serif;
    }

    .metric-card-name {
      font-size: 11px;
      font-weight: 600;
      color: var(--ink);
      margin-bottom: 4px;
    }

    .metric-card-value {
      font-size: 16px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 6px;
    }

    .metric-card-zscore {
      font-size: 10px;
      color: #999;
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
    }

    .metric-label-left {
      text-align: left;
    }

    .metric-percentile-right {
      text-align: right;
    }

    .metric-card-bar {
      margin-bottom: 6px;
    }

    .metric-card-bar-background {
      height: 4px;
      background: #e0e0e0;
      border-radius: 2px;
      position: relative;
    }

    .metric-card-bar-center {
      position: absolute;
      top: 0;
      left: 50%;
      height: 100%;
      width: 1px;
      background: #999;
    }

    .metric-card-bar-fill {
      position: absolute;
      height: 100%;
      border-radius: 2px;
    }

    .metric-card-bar-labels {
      font-size: 8px;
      color: #999;
      display: flex;
      justify-content: space-between;
    }

    .metric-card-bar-label-left {
      text-align: left;
    }

    .metric-card-bar-label-right {
      text-align: right;
    }

    .s21-minutes-warning-text {
      color: #e74c3c !important;
    }

    .s21-minutes-value {
      font-weight: 700;
      color: var(--ink);
    }

    @media print {
      .s21-radar-section {
        page-break-inside: avoid;
      }
    }
    </style>
    """
