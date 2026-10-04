#!/usr/bin/env python3
"""Section 15: Pressure Heatmap."""

from .charts import create_heatmap_chart, create_discipline_score_chart, create_card_counter_chart
from event_based.metrics import Metric


def get_styles() -> str:
    """Get CSS styles for this section."""
    return """<style>
.section15-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.section15-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin-bottom: 10px;
    text-transform: capitalize;
}

.section15-heatmap-wrapper {
    display: flex;
    gap: 30px;
    justify-content: center;
    align-items: flex-start;
}

.section15-charts-row {
    display: flex;
    gap: 20px;
    justify-content: center;
    align-items: flex-start;
    width: 100%;
}

.section15-chart-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}

.section15-heatmap-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    position: relative;
}

.section15-heatmap-with-arrow {
    position: relative;
    display: inline-block;
}

.section15-heatmap-label {
    font-size: 12px;
    font-weight: 600;
    color: #333;
}

.section15-heatmap-stats {
    font-size: 11px;
    color: #666;
    margin-top: 8px;
    padding: 12px;
    background: #f9f9f9;
    border-radius: 6px;
    text-align: center;
}

.section15-stat-item {
    display: flex;
    justify-content: center;
    margin-bottom: 6px;
}

.section15-stat-item:last-child {
    margin-bottom: 0;
}

.section15-stat-label {
    color: #999;
    margin-right: 8px;
}

.section15-stat-value {
    font-weight: 600;
    color: #333;
}

.heatmap-chart {
    display: block;
    margin: 0 auto;
}

.heatmap-arrow-overlay {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(255, 255, 255, 0.9);
    padding: 8px 12px;
    border-radius: 4px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 600;
    color: #333;
}

.heatmap-arrow-icon {
    font-size: 16px;
}
</style>"""


def render_pressure_heatmap_section(team_metrics: dict, team_name: str) -> str:
    """
    Render pressure heatmap section.

    Args:
        team_metrics: Team metrics from event data
        team_name: Name of the team

    Returns:
        HTML string for the section
    """
    # Get metrics
    pressure_heatmap = team_metrics.get('pressure_heatmap')
    pressure_total = team_metrics.get('pressure_total')
    discipline_score = team_metrics.get('discipline_score')
    yellow_card_total = team_metrics.get('yellow_card_total')
    red_card_total = team_metrics.get('red_card_total')

    # Create heatmap chart
    if pressure_heatmap and pressure_heatmap.heatmap:
        pressure_heatmap_chart = create_heatmap_chart(pressure_heatmap,high_resolution=False)
    else:
        pressure_heatmap_chart = '<p style="color: #999; font-style: italic;">No pressure data available.</p>'

    # Build stats display
    stats_html = ""
    if pressure_total:
        total_count = int(pressure_total.value)
        per_game = round(pressure_total.average, 1)

        stats_html = f"""
    <div class="section15-heatmap-stats">
        <div class="section15-stat-item">
            <span class="section15-stat-label">Total Pressures:</span>
            <span class="section15-stat-value">{total_count}</span>
        </div>
        <div class="section15-stat-item">
            <span class="section15-stat-label">Per Match:</span>
            <span class="section15-stat-value">{per_game}</span>
        </div>
    </div>
    """

    # Create discipline and card charts
    discipline_chart = create_discipline_score_chart(discipline_score) if discipline_score else ""
    card_chart = create_card_counter_chart(yellow_card_total, red_card_total) if (yellow_card_total or red_card_total) else ""

    html = f"""
    <div class="section15-container">
        <div class="section15-heatmap-wrapper">            
            <div class="section15-heatmap-container">                
                <br/>
                <br/>
                <div class="section15-heatmap-label">Pressure Locations Across Pitch</div>
                <div class="section15-heatmap-with-arrow">
                    {pressure_heatmap_chart}
                    <div class="heatmap-arrow-overlay">
                        <span class="heatmap-arrow-icon">→</span>
                        <span>Attacking</span>
                    </div>
                </div>
                {stats_html}
            </div>
            <div class="section15-chart-box">
                <br/>
                <br/>
                {discipline_chart}
                {card_chart}
            </div>
        </div>
    </div>
    """

    return html
