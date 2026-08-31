"""Aerial Attack findings."""

from .xg_findings_base import Finding, register_evaluator, register_evidence
from typing import Dict, List


def get_aerial_evidence(finding_name: str, team_metrics: Dict) -> str:
    """Return evidence for aerial attack findings."""
    def get_value(metric_obj):
        return metric_obj.value if hasattr(metric_obj, 'value') else 0.0

    evidence_map = {
        "Strong aerial scoring threat": lambda: f"xG Headers: {get_value(team_metrics.get('xgf_headers')):.2f}",
        "Low aerial threat": lambda: f"xG Headers: {get_value(team_metrics.get('xgf_headers')):.2f}",
    }

    if finding_name in evidence_map:
        try:
            return evidence_map[finding_name]()
        except:
            return None
    return None


def evaluate_aerial_attack(team_id: int, team_name: str, team_metrics: Dict,
                           get_value, get_pct) -> List[Finding]:
    """Evaluate aerial attack findings."""
    findings = []
    xgf_headers_val = get_value(team_metrics.get('xgf_headers'))

    if xgf_headers_val >= 0.5:
        findings.append(Finding(
            category="Aerial Attack",
            finding_name="Strong aerial scoring threat",
            description="Headers contribute substantial attacking xG.",
            team_id=team_id,
            team_name=team_name
        ))
    if xgf_headers_val <= 0.1:
        findings.append(Finding(
            category="Aerial Attack",
            finding_name="Low aerial threat",
            description="Headers contribute little attacking xG.",
            team_id=team_id,
            team_name=team_name
        ))

    return findings

# Register this module's functions
register_evaluator(evaluate_aerial_attack)
register_evidence(get_aerial_evidence)
