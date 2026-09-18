#!/usr/bin/env python3
"""Section 11: Aerial Wins Across Thirds."""

from .charts import create_thirds_chart, create_heatmap_chart
from football_analytics.event_based.metrics import Metric


def get_styles() -> str:
    """Get CSS styles for this section."""
    return """<style>
.section11-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.section11-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin-bottom: 10px;
    text-transform: capitalize;
}

.section11-charts-wrapper {
    display: flex;
    gap: 30px;
    justify-content: center;
    align-items: flex-start;
}

.section11-chart-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.section11-chart-label {
    font-size: 11px;
    color: #666;
    margin-bottom: 8px;
    font-weight: 500;
}

.thirds-chart {
    display: block;
    margin: 0 auto;
}

.section11-heatmap-wrapper {
    display: flex;
    gap: 30px;
    justify-content: center;
    align-items: flex-start;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #e0e0e0;
}

.section11-heatmap-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

.section11-heatmap-label {
    font-size: 12px;
    font-weight: 600;
    color: #333;
}

.heatmap-chart {
    display: block;
    margin: 0 auto;
}
</style>"""


def render_aerial_thirds_section(team_metrics, statsbomb_team_metrics, team_name: str) -> str:
    """
    Render aerial wins across thirds section with two thirds charts side by side.

    Args:
        team_metrics: Team metrics from event data
        statsbomb_team_metrics: StatsBomb team metrics
        team_name: Name of the team

    Returns:
        HTML string for the section
    """
    # Get the metrics for aerial won by third (using ratio metrics)
    defensive_aerial = team_metrics.get('aerial_won_defensive_third_ratio')
    middle_aerial = team_metrics.get('aerial_won_middle_third_ratio')
    final_aerial = team_metrics.get('aerial_won_final_third_ratio')

    if defensive_aerial:
        defensive_aerial.show_as_percentage = True
    if middle_aerial:
        middle_aerial.show_as_percentage = True
    if final_aerial:
        final_aerial.show_as_percentage = True

    # Fallback to default metrics if not found
    if defensive_aerial is None:
        defensive_aerial = Metric.default()
    if middle_aerial is None:
        middle_aerial = Metric.default()
    if final_aerial is None:
        final_aerial = Metric.default()

    # Get the metrics for high pass ratio by third
    defensive_high_pass = team_metrics.get('high_pass_ratio_defensive_third')
    middle_high_pass = team_metrics.get('high_pass_ratio_middle_third')
    final_high_pass = team_metrics.get('high_pass_ratio_final_third')

    if defensive_high_pass:
        defensive_high_pass.show_as_percentage = True
    if middle_high_pass:
        middle_high_pass.show_as_percentage = True
    if final_high_pass:
        final_high_pass.show_as_percentage = True

    # Fallback to default metrics if not found
    if defensive_high_pass is None:
        defensive_high_pass = Metric.default()
    if middle_high_pass is None:
        middle_high_pass = Metric.default()
    if final_high_pass is None:
        final_high_pass = Metric.default()

    # Generate first thirds chart (aerial won ratios)
    first_chart = create_thirds_chart(
        defensive_metric=defensive_aerial,
        middle_metric=middle_aerial,
        final_metric=final_aerial
    )

    # Generate second thirds chart (high pass ratios)
    second_chart = create_thirds_chart(
        defensive_metric=defensive_high_pass,
        middle_metric=middle_high_pass,
        final_metric=final_high_pass
    )

    # Get throw-in landing box heatmap metric
    throw_in_landing_box = team_metrics.get('throw_in_landing_box_total')
    if throw_in_landing_box is None:
        throw_in_landing_box = Metric.default()
        throw_in_landing_box.heatmap = Metric.create_empty_heatmap()

    throw_in_landing_box_ratio = team_metrics.get('throw_in_landing_box_ratio')
    if throw_in_landing_box_ratio is None:
        throw_in_landing_box_ratio = Metric.default()
    else:
        throw_in_landing_box_ratio.show_as_percentage = True 

    # Generate heatmap chart for throw-in landing locations
    throw_in_heatmap_chart = create_heatmap_chart(throw_in_landing_box, throw_in_landing_box_ratio, True)
    # Generate heatmap chart for corner landing locations
    left_corner_landing_box = team_metrics.get('left_corner_total')
    if left_corner_landing_box is None:
        left_corner_landing_box = Metric.default()
        left_corner_landing_box.heatmap = Metric.create_empty_heatmap()

    right_corner_landing_box = team_metrics.get('right_corner_total')
    if right_corner_landing_box is None:
        right_corner_landing_box = Metric.default()
        right_corner_landing_box.heatmap = Metric.create_empty_heatmap()

    corner_heatmap_chart = create_heatmap_chart(left_corner_landing_box, None, True, reverse_metric=right_corner_landing_box, metric_label="Right Side Corners", reverse_label="Left Side Corners")

    html = f"""
    <div class="section11-container">

        <div class="section11-charts-wrapper">
            <div class="section11-chart-item">
                <div class="section11-chart-label">Aerial Won Across Thirds</div>
                {first_chart}
            </div>

            <div class="section11-chart-item">
                <div class="section11-chart-label">High Pass Ratio by Zone</div>
                {second_chart}
            </div>
        </div>

        <div class="section11-heatmap-wrapper">
            <div class="section11-heatmap-container">
                <div class="section11-heatmap-label">Throw-in Analysis</div>
                {throw_in_heatmap_chart}
            </div>

            <div class="section11-heatmap-container">
                <div class="section11-heatmap-label">Corner Analysis</div>
                {corner_heatmap_chart}
            </div>
        </div>
    </div>
    """

    return html
