#!/usr/bin/env python3
"""Section 2: Key Insights from metrics analysis."""

from .insights_engine import InsightGenerator


def get_styles() -> str:
    """Get CSS styles for this section."""
    return """<style>
.section2-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding-left: 20px;
    padding-right: 20px;
}

.section2-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin-top: 0;
    margin-bottom: 15px;
    margin-left: 0;
    margin-right: 0;
}

.insights-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

.insight-card {
    background: #f8f9fa;
    border-left: 4px solid #333;
    padding: 15px;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.insight-card.strength {
    border-left-color: #27ae60;
}

.insight-card.concern {
    border-left-color: #e74c3c;
}

.insight-card.tactical {
    border-left-color: #3498db;
}

.insight-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.insight-card.strength .insight-label {
    color: #27ae60;
}

.insight-card.concern .insight-label {
    color: #e74c3c;
}

.insight-card.tactical .insight-label {
    color: #3498db;
}

.insight-text {
    font-size: 13px;
    color: #555;
    line-height: 1.5;
}

.insight-section-header {
    font-size: 15px;
    font-weight: 600;
    color: #333;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #ddd;
}

@media (max-width: 1024px) {
    .insights-grid {
        grid-template-columns: 1fr;
    }
}
</style>"""


def render_insights_section(team_metrics: dict, team_name: str = "", league_table: dict = None, statsbomb_team_metrics: dict = None) -> str:
    """
    Render key insights section.

    Args:
        team_metrics: Team metrics from event data
        team_name: Name of the team
        league_table: League standings for context
        statsbomb_team_metrics: StatsBomb API team metrics (includes possession %)

    Returns:
        HTML string for the section
    """
    generator = InsightGenerator(team_metrics, league_table, team_name, statsbomb_team_metrics)
    insights = generator.generate_insights()
    print("******************************** THIS SHOULDN NOT RUN ********************************")

    html = """
    <div class="section2-container">
        <h2 class="s13-section-title">Key Insights</h2>
        <p class="s13-section-subtitle">Performance analysis across attacking, possession and defensive metrics</p>
    """

    # Render each section (Attacking, Possession, Defense)
    for section_name, section_insights in insights.items():
        html += f"""
        <div>
            <div class="insight-section-header">{section_name}</div>
            <div class="insights-grid">
    """

        for category in ["Strength", "Concern", "Tactical"]:
            insight_text = section_insights.get(category, "")
            html += f"""
                <div class="insight-card {category.lower()}">
                    <div class="insight-label">{category}</div>
                    <div class="insight-text">{insight_text}</div>
                </div>
        """

        html += """
            </div>
        </div>
        """

    html += """
    </div>
    """

    return html
