"""
XG Findings Layer: Orchestrates findings evaluation across category modules.

Uses registry pattern - each category module registers itself when imported.
To add a new category:
  1. Create xg_findings_mycategory.py with evaluate_* and get_*_evidence functions
  2. Add registration calls: register_evaluator(...) and register_evidence(...)
  3. Import it here
"""

from typing import Dict, List
from .xg_findings_base import Finding, get_finding_evidence, get_evaluators

# Import all category modules to trigger registration
from . import (
    xg_findings_attacking,
    xg_findings_chance_creation,
    xg_findings_chance_quality,
    xg_findings_attacking_profile,
    xg_findings_set_pieces,
    xg_findings_finishing,
    xg_findings_aerial,
    xg_findings_defending,
)


class XGFindingsLayer:
    """Evaluates xG metrics against comprehensive findings catalog."""

    def __init__(self):
        self.layer_name = "xg_findings"

    def evaluate_team(self, team_id: int, team_name: str, team_metrics: Dict) -> List[Finding]:
        """
        Evaluate all findings for a team.

        Args:
            team_id: Team identifier
            team_name: Team name
            team_metrics: Team's aggregated metrics with Metric objects

        Returns:
            List of triggered findings for this team
        """
        findings = []

        def get_value(metric_obj):
            """Extract value from Metric object."""
            return metric_obj.value if hasattr(metric_obj, 'value') else 0.0

        def get_pct(metric_obj):
            """Extract percentile from Metric object."""
            return metric_obj.percentile if hasattr(metric_obj, 'percentile') else 0.0

        # Call all registered evaluators
        for evaluator in get_evaluators():
            try:
                findings.extend(evaluator(team_id, team_name, team_metrics, get_value, get_pct))
            except Exception:
                pass

        return findings

    def process_event_row(self, event_row: Dict, accumulator, team_ids: Dict = None):
        """Not used for findings layer."""
        pass

    def aggregate(self, team_aggregates: Dict, team_id: int, match_data: Dict) -> None:
        """Not used for findings layer."""
        pass


__all__ = ['Finding', 'get_finding_evidence', 'XGFindingsLayer']
