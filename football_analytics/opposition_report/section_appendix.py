#!/usr/bin/env python3
"""Section Appendix: Metrics reference guide for all report sections."""


def get_styles() -> str:
    """Get CSS styles for appendix section."""
    return """<style>
.appendix-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding-left: 20px;
    padding-right: 20px;
    margin-top: 40px;
    padding-top: 40px;
    border-top: 2px solid #e5e5e5;
}

.appendix-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin-top: 0;
    margin-bottom: 15px;
}

.appendix-subtitle {
    font-size: 14px;
    color: #666;
    margin-bottom: 20px;
    font-style: italic;
}

.metrics-table {
    border-collapse: collapse;
    width: 100%;
}

.metrics-table tr {
    border-bottom: 1px solid #e5e5e5;
}

.metrics-table tr:last-child {
    border-bottom: none;
}

.metrics-table td {
    padding: 10px 0;
    font-size: 13px;
}

.metric-name-col {
    width: 35%;
    font-weight: 600;
    color: #2c3e50;
    padding-right: 20px;
}

.metric-desc-col {
    width: 65%;
    color: #555;
    line-height: 1.4;
}
</style>"""


def render_appendix_section() -> str:
    """Render appendix with all metrics used in the report, alphabetically ordered."""

    # Display names used in the report, alphabetically ordered
    metrics_data = [
        ("Aerial Duels", "Total number of aerial duels contested across all matches."),
        ("Aerial Win Rate", "Percentage of aerial duels won."),
        ("Card Counter", "Visual representation of yellow and red cards received."),
        ("Counterattack Shots", "Shots generated within 15 seconds from possessions in own half."),
        ("Counterpress pG", "Pressures exerted within 5 seconds of a turnover per game."),
        ("Crosses into Box pG", "Number of crosses into the box per game."),
        ("Deep Completions pG", "Successful passes within 20m of opposition goal per game."),
        ("Deep Progression", "Passes, dribbles and carries into opposition final third per game."),
        ("Discipline Score", "Calculated metric showing defensive discipline: (4 × red cards) + yellow cards."),
        ("Dribble Ratio", "Percentage of dribble attempts completed."),
        ("Dribbles pG", "Total dribble attempts per game."),
        ("F.Half Press Ratio", "Percentage of pressures exerted in opposition half."),
        ("F.Third Passes", "Completed passes in opposition final third across all matches."),
        ("Finishing", "Goals per expected goal (conversion efficiency) tracked per match."),
        ("High Pass Ratio", "Percentage of high passes that were completed successfully."),
        ("Interceptions", "Ball interceptions - tracked per match for positioning quality trend."),
        ("np xG pG", "Non-penalty expected goals per game."),
        ("Passes into Box pG", "Completed passes inside the box per game."),
        ("Possession", "Average possession percentage maintained per match."),
        ("Pressure", "Pressure application count - tracked per match for pressing intensity trend."),
        ("Pressure Heatmap", "Spatial heatmap showing locations where pressure is applied (4m×4m grid)."),
        ("Pressure Regains vs Pressures", "Scatter chart comparing ball regains from pressing vs total pressure events."),
        ("Red Cards", "Total red cards received across all matches."),
        ("Regains from CP pG", "Ball regains within 5 seconds of counterpressing per game."),
        ("Regains pG", "Ball regains within 5 seconds of defensive actions per game."),
        ("Shot Distance", "Average distance from goal for open play shots (in meters)."),
        ("Shots", "Total shots - tracked per match to identify shooting trend."),
        ("Shots Conceded from press", "Shots conceded from possessions lost in own half per game."),
        ("Tackles", "Tackle count - tracked per match for defensive engagement trend."),
        ("xG Scatter Chart", "Comparative chart showing expected goals for vs expected goals against."),
        ("xGD pG", "Expected goals difference (xG minus xG conceded) per game."),
        ("xGA Set Piece", "Expected goals conceded from set piece situations across all matches."),
        ("Yellow Cards", "Total yellow cards received across all matches."),
    ]

    html = f"""
    <section class="appendix-container">
        <h2 class="appendix-title">Appendix: Metrics Reference</h2>
        <p class="appendix-subtitle">Complete list of metrics displayed throughout this opposition report</p>

        <table class="metrics-table">
    """

    for metric_name, description in metrics_data:
        html += f"""
            <tr>
                <td class="metric-name-col">{metric_name}</td>
                <td class="metric-desc-col">{description}</td>
            </tr>
        """

    html += """
        </table>
    </section>
    """

    return html
