"""
BaseKPIPlugin
-------------
Abstract base class that every KPI plugin must implement.

A plugin is a self-contained analytical module that:
    - Declares what data fields it requires
    - Declares what report contexts it applies to (via tags)
    - Checks whether it can run against a PreparedDataset
    - Calculates its indicators and generates findings
    - Returns a structured KPIResult

Plugins know nothing about the report layer or other plugins.
They receive a PreparedDataset and return a KPIResult. That is all.

Adding a new metric = adding a new plugin file + registering it.
No other layer needs to change.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


# ---------------------------------------------------------------------------
# KPI output contracts
# ---------------------------------------------------------------------------

@dataclass
class Indicator:
    """
    A single calculated metric within a KPI plugin.

    'value' is the raw number.
    'display' is the formatted string for the report.
    'interpretation' is a short human-readable verdict.
    """
    id: str
    label: str
    value: float
    display: str
    interpretation: str                         # e.g. 'overperforming', 'on_par', 'underperforming'
    confidence: float                           # inherited from DataRecipe
    context: Optional[dict[str, Any]] = None   # additional breakdown data
    percentile: Optional[float] = None         # percentile rank within league/position group
    benchmark: Optional[float] = None          # league average for comparison


@dataclass
class KPIResult:
    """
    The output contract of every KPI plugin.

    'findings' lead the report section — they are the narrative.
    'indicators' support the findings — they are the evidence.
    """
    plugin_id: str
    display_name: str
    indicators: list[Indicator]
    findings: list[str]                         # natural language insight statements
    confidence: float
    confidence_level: str                       # 'low' | 'medium' | 'high'
    flags: list[str]
    required_sample_met: bool
    tags: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Base plugin
# ---------------------------------------------------------------------------

class BaseKPIPlugin(ABC):
    """
    Abstract base class for all KPI plugins.

    Class-level attributes (set on each subclass, not instances):
        plugin_id       — unique identifier e.g. 'xg_team'
        display_name    — human-readable e.g. 'Expected Goals — Team'
        required_fields — PreparedDataset attributes this plugin needs
        min_sample_size — minimum games before results are meaningful
        tags            — used by ContextEngine to select relevant plugins

    Valid tags:
        Scope:    'team', 'player'
        Domain:   'attacking', 'defensive', 'set_piece', 'tactical', 'physical'
        Priority: 'core', 'supplementary', 'experimental'
        Audience: 'recruitment', 'coaching_staff', 'board'
    """

    plugin_id: str = NotImplemented
    display_name: str = NotImplemented
    required_fields: list[str] = []
    min_sample_size: int = 6
    tags: list[str] = []

    @abstractmethod
    def can_run(self, dataset) -> bool:
        """
        Check whether required data is available in the dataset.

        Return True if all required_fields are present and non-empty.
        Return False if the plugin cannot produce meaningful output.
        The ContextEngine will exclude this plugin if can_run returns False.
        """
        pass

    @abstractmethod
    def calculate(self, dataset) -> KPIResult:
        """
        Run all indicators and generate findings.

        Must return a KPIResult. Must not raise — handle exceptions
        internally and return a low-confidence result if needed.

        Findings should lead with insight ('what does this mean?').
        Indicators provide the supporting evidence ('what are the numbers?').
        """
        pass

    # ---------------------------------------------------------------------------
    # Shared helpers available to all plugins
    # ---------------------------------------------------------------------------

    def _check_sample_size(self, n_games: int) -> bool:
        """Return True if the sample meets the minimum requirement."""
        return n_games >= self.min_sample_size

    def _has_required_fields(self, dataset) -> bool:
        """Check all required fields exist and are not None."""
        for field_name in self.required_fields:
            if not hasattr(dataset, field_name):
                return False
            if getattr(dataset, field_name) is None:
                return False
        return True

    def _percentile_rank(self, value: float, distribution: list[float]) -> float:
        """
        Calculate the percentile rank of a value within a distribution.
        Returns a float 0.0–100.0.
        """
        if not distribution:
            return 50.0
        below = sum(1 for v in distribution if v < value)
        return round((below / len(distribution)) * 100, 1)

    def _format_sign(self, value: float, decimals: int = 2) -> str:
        """Format a float with explicit sign. e.g. +1.23 or -0.45"""
        return f"{'+' if value >= 0 else ''}{value:.{decimals}f}"

    def _build_low_confidence_result(self, reason: str) -> KPIResult:
        """
        Return a minimal KPIResult when the plugin cannot run properly.
        Ensures the pipeline never crashes on a plugin failure.
        """
        return KPIResult(
            plugin_id=self.plugin_id,
            display_name=self.display_name,
            indicators=[],
            findings=[f"Insufficient data: {reason}"],
            confidence=0.0,
            confidence_level='low',
            flags=['insufficient_data'],
            required_sample_met=False,
            tags=self.tags,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.plugin_id}', tags={self.tags})"
