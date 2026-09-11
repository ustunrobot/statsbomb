"""Chance Quality findings."""

from typing import Dict, List
from .xg_findings_base import Finding, register_evaluator, register_evidence, get_metric, create_percentile_findings


def get_chance_quality_evidence(finding_name: str, team_metrics: Dict) -> str:
    """Return evidence for chance quality findings."""
    def get_value(metric_obj):
        return metric_obj.value if hasattr(metric_obj, 'value') else 0.0
    def get_pct(metric_obj):
        return metric_obj.percentile if hasattr(metric_obj, 'percentile') else 0.0

    xgf_per_shot = get_metric(team_metrics, 'xgf_per_shot') or team_metrics.get('xgf_per_shot')
    xgf_open_play_per_open_shots = get_metric(team_metrics, 'xgf_open_play_per_open_shots') or team_metrics.get('xgf_open_play_per_open_shots')

    evidence_map = {
        "High shot quality": lambda: f"xG/Shot: {get_value(xgf_per_shot):.3f} ({get_pct(xgf_per_shot):.0f}th %ile)",
        "Low shot quality": lambda: f"xG/Shot: {get_value(xgf_per_shot):.3f} ({get_pct(xgf_per_shot):.0f}th %ile)",
        "High open play shot quality": lambda: f"Open Play xG/Shot: {get_value(xgf_open_play_per_open_shots):.3f} ({get_pct(xgf_open_play_per_open_shots):.0f}th %ile)",
        "Low open play shot quality": lambda: f"Open Play xG/Shot: {get_value(xgf_open_play_per_open_shots):.3f} ({get_pct(xgf_open_play_per_open_shots):.0f}th %ile)",
    }

    if finding_name in evidence_map:
        try:
            return evidence_map[finding_name]()
        except:
            return None
    return None


def evaluate_chance_quality(team_id: int, team_name: str, team_metrics: Dict,
                            get_value, get_pct) -> List[Finding]:
    """Evaluate shot quality findings."""
    findings = []
    category = "Chance Quality"

    xgf_per_shot_pct = get_pct(get_metric(team_metrics, 'xgf_per_shot') or team_metrics.get('xgf_per_shot'))
    xgf_open_play_per_open_shots_pct = get_pct(get_metric(team_metrics, 'xgf_open_play_per_open_shots') or team_metrics.get('xgf_open_play_per_open_shots'))

    findings.extend(create_percentile_findings(xgf_per_shot_pct, 80, 20, "shot quality", category, team_id, team_name))
    findings.extend(create_percentile_findings(xgf_open_play_per_open_shots_pct, 80, 20, "open play shot quality", category, team_id, team_name))

    return findings


# Register this module's functions
register_evaluator(evaluate_chance_quality)
register_evidence(get_chance_quality_evidence)
