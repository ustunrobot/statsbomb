#!/usr/bin/env python3
"""Section 16: Performance trends showing metric values over periods."""

from copy import deepcopy
from .charts import create_trend_chart
from ..event_based.metrics import Metric


def get_styles() -> str:
    """Get CSS styles for this section."""
    return """<style>
.section16-container {
    display: flex;
    flex-direction: column;
    padding-left: 50px;
    padding-right: 20px;
    padding-top: 30px;

}

.section16-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin-top: 0;
    margin-bottom: 15px;
    margin-left: 0;
    margin-right: 0;
}

.section16-charts-row {
    display: flex;
    gap: 30px;
    justify-content: center;
    align-items: flex-start;
}

.section16-chart-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

.trend-chart {
    display: block;
    margin: 0 auto;
}
</style>"""


def _extract_periods(value_trend, reverse: bool):
    """
    Extract 4 periods from value_trend list.

    Args:
        value_trend: List of per-match values
        metric_name: Name of metric (for debugging)

    Returns:
        List of 4 values: [past_avg, last_2, last_1, last]
    """
    if not value_trend:
        return [None, None, None, None]

    values = deepcopy(value_trend)

    # Reverse values if needed (for metrics where higher is worse)
    if reverse:
        values = [v * -1 if v is not None else None for v in values]

    # Handle different lengths
    if len(values) == 1:        
        return [None, None, None, values[0]]
    elif len(values) == 2:    
        return [None, None, values[0], values[1]]
    elif len(values) == 3:        
        return [None, values[0], values[1], values[2]]
    else:
        # 4 or more values
        past_values = values[:-3]
        past_avg = sum(past_values) / len(past_values) if past_values else None
        result = [
            past_avg,
            values[-3],
            values[-2],
            values[-1]
        ]        
        return result


def render_performance_trends_section(team_metrics: dict, team_name: str) -> str:
    """
    Render performance trend charts section.

    Args:
        team_metrics: Team metrics from event data
        team_name: Name of the team

    Returns:
        HTML string for the section
    """
    # Extract trend data for attacking metrics
    attacking_metrics = {
        "xGF": team_metrics.get("xg_for_total"),
        "Shots": team_metrics.get("shot_for_total"),
    }

    # Calculate Finishing (Goals/xGF) from value_trends
    xgf_metric = team_metrics.get("xg_for_total")
    goals_metric = team_metrics.get("goal_for_total")

    if xgf_metric and goals_metric and xgf_metric.value_trend and goals_metric.value_trend:
        # Calculate Goals/xGF for each match
        finishing_values = []
        for goals_val, xgf_val in zip(goals_metric.value_trend, xgf_metric.value_trend):
            if xgf_val > 0:
                finishing_values.append(goals_val / xgf_val)
            else:
                finishing_values.append(0)

        # Create a temporary metric object for Finishing
        finishing_metric = Metric.default()
        finishing_metric.value_trend = finishing_values
        attacking_metrics["Finishing"] = finishing_metric

    attacking_series = {}
    for name, metric in attacking_metrics.items():
        if metric and metric.value_trend:
            periods = _extract_periods(metric.value_trend, False)
            attacking_series[name] = periods

    # Extract trend data for defensive metrics
    defensive_metrics = {
        "Pressure": team_metrics.get("pressure_total"),
        "Shots Against": team_metrics.get("shot_against_total"),
        "xG Against": team_metrics.get("xg_against_total"),
    }

    defensive_series = {}
    for name, metric in defensive_metrics.items():
        if metric and metric.value_trend:
            if name == "Pressure":
                periods = _extract_periods(metric.value_trend, False)
            else:
                periods = _extract_periods(metric.value_trend, True)
            defensive_series[name] = periods

    # Create charts only if we have data
    attacking_chart = ""
    defensive_chart = ""

    if attacking_series:
        attacking_chart = create_trend_chart(attacking_series, "Attacking Performance Trend")
    if defensive_series:
        defensive_chart = create_trend_chart(defensive_series, "Defensive Performance Trend")

    if not attacking_chart and not defensive_chart:
        return f"""
    <div class="section16-container">
        <div class="section16-title">Performance Trends</div>
        <p style="color: #999; font-style: italic;">No trend data available.</p>
    </div>
    """

    html = f"""
    <div class="section16-container">
        <h2 class="s13-section-title">Trends</h2>
        <p class="s13-section-subtitle">Trend analysis of overall performance metrics</p>
        <div class="section16-charts-row">
            <div class="section16-chart-box">
                {attacking_chart}
            </div>
            <div class="section16-chart-box">
                {defensive_chart}
            </div>
        </div>
    </div>
    """

    return html
