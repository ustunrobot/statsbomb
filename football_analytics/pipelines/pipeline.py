"""
Football Intelligence Platform — Pipeline Orchestrator
-------------------------------------------------------
Entry point. Wires all layers together and executes the full
analysis pipeline from a ReportRequest through to a Report.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from context_resolver.context_resolver_engine import ContextResolverEngine
from data_prep.data_prep_engine import DataPrepEngine
from kpi.plugin_registry import PLUGIN_REGISTRY
from context.context_engine import ContextEngine, ReportContext
from report.report_builder import ReportBuilder, Report


# ---------------------------------------------------------------------------
# Request definition
# ---------------------------------------------------------------------------

@dataclass
class ReportRequest:
    """
    Describes what report to generate and for whom.
    Constructed by the caller (API handler, CLI, scheduler, etc.)
    and passed unchanged into the pipeline.
    """
    entity_id: str                      # team_id or player_id
    entity_type: str                    # 'team' | 'player'
    report_type: str                    # 'team_analysis' | 'player_analysis'
                                        # | 'opposition_scout' | 'recruitment'
    season_current: str                 # e.g. '2025-26'
    season_prior: str                   # e.g. '2024-25'
    game_week: int
    audience: str                       # 'coaching_staff' | 'recruitment' | 'board'
    focus: Optional[list[str]] = None   # e.g. ['attacking', 'set_piece']
    league_id: Optional[str] = None
    requested_at: datetime = None

    def __post_init__(self):
        self.focus = self.focus or []
        self.requested_at = self.requested_at or datetime.now()


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class FootballIntelligencePipeline:
    """
    Orchestrates the five layers in sequence.
    Each layer receives only what it needs — no layer reaches past its neighbour.

    Flow:
        ReportRequest
            → ContextResolver  (assess data trustworthiness, build DataRecipe)
            → DataPrepEngine   (fetch, blend, normalise raw data)
            → ContextEngine    (select relevant KPI plugins)
            → KPI Plugins      (calculate indicators and findings)
            → ReportBuilder    (assemble final Report)
    """

    def __init__(self):
        self.context_resolver = ContextResolverEngine()
        self.data_prep = DataPrepEngine()
        self.context_engine = ContextEngine()
        self.report_builder = ReportBuilder()

    def run(self, request: ReportRequest) -> Report:
        """Execute the full pipeline and return a Report."""

        # 1. Resolve context — assess continuity, produce DataRecipe
        recipe = self.context_resolver.assess(request)

        # 2. Prepare data — fetch, blend, normalise using the recipe
        dataset = self.data_prep.prepare(recipe, request)

        # 3. Select plugins — context-aware plugin selection
        report_context = ReportContext(
            report_type=request.report_type,
            entity_id=request.entity_id,
            entity_type=request.entity_type,
            focus=request.focus,
            audience=request.audience,
            game_week=request.game_week,
            flags=recipe.flags,
        )
        plugins = self.context_engine.select_plugins(
            report_context, dataset, PLUGIN_REGISTRY
        )

        # 4. Run selected KPI plugins
        kpi_results = []
        for plugin in plugins:
            try:
                result = plugin.calculate(dataset)
                kpi_results.append(result)
            except Exception as e:
                # TODO: replace with proper logging
                print(f"[WARN] Plugin {plugin.plugin_id} failed: {e}")

        # 5. Build and return report
        return self.report_builder.build(report_context, recipe, kpi_results)


# ---------------------------------------------------------------------------
# CLI entry point (for local testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    request = ReportRequest(
        entity_id="team_001",
        entity_type="team",
        report_type="team_analysis",
        season_current="2025-26",
        season_prior="2024-25",
        game_week=4,
        audience="coaching_staff",
        focus=["attacking", "defensive"],
        league_id="epl",
    )

    pipeline = FootballIntelligencePipeline()
    report = pipeline.run(request)
    print(report)
