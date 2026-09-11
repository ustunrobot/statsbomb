"""Finishing findings."""

from .xg_findings_base import Finding, register_evaluator, register_evidence
from typing import Dict, List


def get_finishing_evidence(finding_name: str, team_metrics: Dict) -> str:
    """Return evidence for finishing findings."""
    def get_value(metric_obj):
        return metric_obj.value if hasattr(metric_obj, 'value') else 0.0

    evidence_map = {
        "Clinical finishing": lambda: f"Goals: {get_value(team_metrics.get('goals')):.0f}, xGF: {get_value(team_metrics.get('xgf')):.2f}, Diff: +{get_value(team_metrics.get('goals')) - get_value(team_metrics.get('xgf')):.2f}",
        "Finishing underperformance": lambda: f"Goals: {get_value(team_metrics.get('goals')):.0f}, xGF: {get_value(team_metrics.get('xgf')):.2f}, Diff: {get_value(team_metrics.get('goals')) - get_value(team_metrics.get('xgf')):.2f}",
        "High conversion of shooting opportunities": lambda: f"Conversion: {get_value(team_metrics.get('goals')) / max(1, get_value(team_metrics.get('shots'))) * 100:.1f}%",
        "Low conversion": lambda: f"Conversion: {get_value(team_metrics.get('goals')) / max(1, get_value(team_metrics.get('shots'))) * 100:.1f}%",
    }

    if finding_name in evidence_map:
        try:
            return evidence_map[finding_name]()
        except:
            return None
    return None


def evaluate_finishing(team_id: int, team_name: str, team_metrics: Dict,
                       get_value, get_pct) -> List[Finding]:
    """Evaluate finishing findings."""
    findings = []
    goals_val = get_value(team_metrics.get('goals'))
    xgf_val = get_value(team_metrics.get('xgf'))
    shots_val = get_value(team_metrics.get('shots'))

    goal_diff = goals_val - xgf_val
    if goal_diff >= 1.0:
        findings.append(Finding(
            category="Finishing",
            finding_name="Clinical finishing",
            team_id=team_id,
            team_name=team_name
        ))
    if goal_diff <= -1.0:
        findings.append(Finding(
            category="Finishing",
            finding_name="Finishing underperformance",
            team_id=team_id,
            team_name=team_name
        ))

    if shots_val > 0:
        conversion_rate = goals_val / shots_val
        if conversion_rate >= 0.15:
            findings.append(Finding(
                category="Finishing",
                finding_name="High conversion of shooting opportunities",
                team_id=team_id,
                team_name=team_name
            ))
        if conversion_rate <= 0.05:
            findings.append(Finding(
                category="Finishing",
                finding_name="Low conversion",
                team_id=team_id,
                team_name=team_name
            ))

    return findings

# Register this module's functions
register_evaluator(evaluate_finishing)
register_evidence(get_finishing_evidence)
