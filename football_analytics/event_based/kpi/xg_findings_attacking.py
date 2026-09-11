"""Overall Attacking Performance findings."""

from typing import Dict, List
from .xg_findings_base import Finding, register_evaluator, register_evidence, create_percentile_findings


def get_attacking_evidence(finding_name: str, team_metrics: Dict) -> str:
    """Return evidence for attacking performance findings."""
    def get_value(metric_obj):
        return metric_obj.value if hasattr(metric_obj, 'value') else 0.0
    def get_pct(metric_obj):
        return metric_obj.percentile if hasattr(metric_obj, 'percentile') else 0.0

    xgf = team_metrics.get('xg_for_total')
    goals = team_metrics.get('goal_for_total')
    xgf_minus_goal = team_metrics.get('xgf_minus_goal')

    evidence_map = {
        "High xGF output": lambda: f"xGF: {get_value(xgf):.2f} ({get_pct(xgf):.0f}th %ile)",
        "Low xGF output": lambda: f"xGF: {get_value(xgf):.2f} ({get_pct(xgf):.0f}th %ile)",
        "High goal output": lambda: f"Goals: {get_value(goals):.0f} ({get_pct(goals):.0f}th %ile)",
        "Low goal output": lambda: f"Goals: {get_value(goals):.0f} ({get_pct(goals):.0f}th %ile)",
        "High xGF vs goals scored": lambda: f"Goals vs xG: {get_value(xgf_minus_goal):.2f} ({get_pct(xgf_minus_goal):.0f}th %ile)",
        "Low xGF vs goals scored": lambda: f"Goals vs xG: {get_value(xgf_minus_goal):.2f} ({get_pct(xgf_minus_goal):.0f}th %ile)",
    }

    if finding_name in evidence_map:
        try:
            return evidence_map[finding_name]()
        except:
            return None
    return None


def evaluate_attacking_performance(team_id: int, team_name: str, team_metrics: Dict,
                                   get_value, get_pct) -> List[Finding]:
    """Evaluate overall attacking performance findings."""
    findings = []
    category = "Overall Attacking Performance"

    xgf = team_metrics.get('xg_for_total')
    goals = team_metrics.get('goal_for_total')
    xgf_minus_goal = team_metrics.get('xgf_minus_goal')

    xgf_pct = get_pct(xgf)
    goals_pct = get_pct(goals)
    xgf_minus_goal_pct = get_pct(xgf_minus_goal)

    # xG output (elite threshold: 90, strong: 80, weak: 20, very weak: 10)
    findings.extend(create_percentile_findings(
            xgf_pct, 80, 20, "xGF output", category, team_id, team_name
        ))
    
    # Goal output
    findings.extend(create_percentile_findings(
        goals_pct, 80, 20, "goal output", category, team_id, team_name
    ))

    # Goals vs xG
    findings.extend(create_percentile_findings(
        xgf_minus_goal_pct, 80, 20, "xGF vs goals scored", category, team_id, team_name
    ))

    return findings


# Register this module's functions
register_evaluator(evaluate_attacking_performance)
register_evidence(get_attacking_evidence)
