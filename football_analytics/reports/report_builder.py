"""
ReportBuilder
-------------
Assembles a Report from KPI plugin results.

The report structure always leads with findings (insight),
supported by indicators (evidence). Single metric displays
are never the primary output — see platform philosophy.

Report sections are ordered by plugin priority and confidence.
Low-confidence sections are included but clearly flagged.

The ReportBuilder is output-format agnostic — it produces a
structured Report object. Rendering to JSON, HTML, PDF, or
any other format is the responsibility of downstream renderers.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from kpi.base_plugin import KPIResult, Indicator
from context.context_engine import ReportContext
from context_resolver.data_recipe import DataRecipe


# ---------------------------------------------------------------------------
# Report output contracts
# ---------------------------------------------------------------------------

@dataclass
class ReportSection:
    """
    One section of a report, corresponding to one KPI plugin's output.

    'findings' are the narrative — lead the section.
    'indicators' are the evidence — support the findings.
    """
    plugin_id: str
    title: str
    findings: list[str]
    indicators: list[Indicator]
    confidence: float
    confidence_level: str
    flags: list[str]
    sample_warning: bool
    tags: list[str]


@dataclass
class ReportMetadata:
    """
    Context and provenance metadata attached to every report.
    """
    entity_id: str
    entity_type: str
    report_type: str
    audience: str
    game_week: int
    season: str
    generated_at: datetime
    confidence_level: str               # overall report confidence
    confidence_score: float
    flags: list[str]
    blend_summary: str                  # human-readable data blend description
    sections_included: list[str]        # plugin IDs in this report
    notes: str


@dataclass
class Report:
    """
    The final output of the pipeline.

    Structured for consumption by any rendering layer
    (JSON API, HTML template, PDF generator, etc.)
    """
    metadata: ReportMetadata
    sections: list[ReportSection]

    def get_section(self, plugin_id: str) -> Optional[ReportSection]:
        """Retrieve a section by plugin ID."""
        return next((s for s in self.sections if s.plugin_id == plugin_id), None)

    def has_flag(self, flag: str) -> bool:
        return flag in self.metadata.flags

    def is_low_confidence(self) -> bool:
        return self.metadata.confidence_level == 'low'

    def to_dict(self) -> dict:
        """Serialise to a plain dict for JSON rendering."""
        return {
            'metadata': {
                'entity_id': self.metadata.entity_id,
                'entity_type': self.metadata.entity_type,
                'report_type': self.metadata.report_type,
                'audience': self.metadata.audience,
                'game_week': self.metadata.game_week,
                'season': self.metadata.season,
                'generated_at': self.metadata.generated_at.isoformat(),
                'confidence_level': self.metadata.confidence_level,
                'confidence_score': self.metadata.confidence_score,
                'flags': self.metadata.flags,
                'blend_summary': self.metadata.blend_summary,
                'notes': self.metadata.notes,
            },
            'sections': [
                {
                    'plugin_id': s.plugin_id,
                    'title': s.title,
                    'findings': s.findings,
                    'confidence_level': s.confidence_level,
                    'sample_warning': s.sample_warning,
                    'flags': s.flags,
                    'indicators': [
                        {
                            'id': ind.id,
                            'label': ind.label,
                            'value': ind.value,
                            'display': ind.display,
                            'interpretation': ind.interpretation,
                            'percentile': ind.percentile,
                            'benchmark': ind.benchmark,
                        }
                        for ind in s.indicators
                    ]
                }
                for s in self.sections
            ]
        }

    def __repr__(self) -> str:
        return (
            f"Report(entity={self.metadata.entity_id}, "
            f"type={self.metadata.report_type}, "
            f"gw={self.metadata.game_week}, "
            f"confidence={self.metadata.confidence_level}, "
            f"sections={len(self.sections)})"
        )


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class ReportBuilder:
    """
    Assembles a Report from KPIResults and context metadata.

    Usage:
        builder = ReportBuilder()
        report = builder.build(context, recipe, kpi_results)
    """

    def build(
        self,
        context: ReportContext,
        recipe: DataRecipe,
        kpi_results: list[KPIResult],
    ) -> Report:
        """
        Assemble the final Report.

        Args:
            context:        ReportContext from the ContextEngine
            recipe:         DataRecipe from the ContextResolver
            kpi_results:    List of KPIResult from plugin execution

        Returns:
            Structured Report object
        """
        sections = [
            self._build_section(result)
            for result in kpi_results
        ]

        # Order sections: high confidence first, then by plugin priority
        sections = self._order_sections(sections)

        metadata = ReportMetadata(
            entity_id=context.entity_id,
            entity_type=context.entity_type,
            report_type=context.report_type,
            audience=context.audience,
            game_week=context.game_week,
            season=recipe.season_current,
            generated_at=datetime.now(),
            confidence_level=recipe.confidence_level,
            confidence_score=recipe.confidence_score,
            flags=recipe.flags,
            blend_summary=self._build_blend_summary(recipe),
            sections_included=[r.plugin_id for r in kpi_results],
            notes=recipe.notes,
        )

        return Report(metadata=metadata, sections=sections)

    # ---------------------------------------------------------------------------
    # Private
    # ---------------------------------------------------------------------------

    def _build_section(self, result: KPIResult) -> ReportSection:
        return ReportSection(
            plugin_id=result.plugin_id,
            title=result.display_name,
            findings=result.findings,
            indicators=result.indicators,
            confidence=result.confidence,
            confidence_level=result.confidence_level,
            flags=result.flags,
            sample_warning=not result.required_sample_met,
            tags=result.tags,
        )

    def _order_sections(self, sections: list[ReportSection]) -> list[ReportSection]:
        """
        Order report sections.
        High confidence, core sections first.
        Low confidence or experimental sections last.
        """
        confidence_order = {'high': 0, 'medium': 1, 'low': 2}
        priority_order = {'core': 0, 'supplementary': 1, 'experimental': 2}

        def sort_key(section: ReportSection):
            confidence_rank = confidence_order.get(section.confidence_level, 2)
            priority_rank = next(
                (priority_order[t] for t in section.tags if t in priority_order),
                len(priority_order)
            )
            return (priority_rank, confidence_rank, section.plugin_id)

        return sorted(sections, key=sort_key)

    def _build_blend_summary(self, recipe: DataRecipe) -> str:
        """
        Produce a human-readable one-liner describing the data blend.
        Surfaced in the report metadata for transparency.
        """
        parts = []
        if recipe.weight_current_season > 0:
            parts.append(
                f"current season {recipe.weight_current_season:.0%}"
            )
        if recipe.weight_prior_season > 0:
            parts.append(
                f"prior season {recipe.weight_prior_season:.0%}"
            )
        if recipe.weight_coach_history > 0:
            parts.append(
                f"coach history {recipe.weight_coach_history:.0%}"
            )
        return "Data blend: " + " | ".join(parts) if parts else "Data blend: current season only"
