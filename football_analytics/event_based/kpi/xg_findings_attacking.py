"""Overall Attacking Performance findings."""

from typing import Dict, List
from .xg_findings_base import Finding, register_evaluator, register_evidence


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
        "Elite attacking output": lambda: f"xGF: {get_value(xgf):.2f} ({get_pct(xgf):.0f}th %ile)",
        "Strong attacking output": lambda: f"xGF: {get_value(xgf):.2f} ({get_pct(xgf):.0f}th %ile)",
        "Very weak attacking output": lambda: f"xGF: {get_value(xgf):.2f} ({get_pct(xgf):.0f}th %ile)",
        "Weak attacking output": lambda: f"xGF: {get_value(xgf):.2f} ({get_pct(xgf):.0f}th %ile)",
        "Low Goal output": lambda: f"Goals: {get_value(goals):.0f} ({get_pct(goals):.0f}th %ile)",
        "High Goal output": lambda: f"Goals: {get_value(goals):.0f} ({get_pct(goals):.0f}th %ile)",
        "Goals outperforming Process": lambda: f"Goals vs xG: +{get_value(xgf_minus_goal):.2f} ({get_pct(xgf_minus_goal):.0f}th %ile)",
        "Goals underperforming Process": lambda: f"Goals vs xG: {get_value(xgf_minus_goal):.2f} ({get_pct(xgf_minus_goal):.0f}th %ile)",
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

    xgf = team_metrics.get('xg_for_total')
    goals = team_metrics.get('goal_for_total')
    xgf_minus_goal = team_metrics.get('xgf_minus_goal')


    xgf_pct = get_pct(xgf)
    goals_pct = get_pct(goals)
    xgf_minus_goal_pct = get_pct(xgf_minus_goal)

    if xgf_pct >= 90:
        findings.append(Finding(
            category="Overall Attacking Performance",
            finding_name="Elite attacking output",
            description="Exceptional expected-goal production.",
            team_id=team_id,
            team_name=team_name
        ))
    elif xgf_pct >= 80:
        findings.append(Finding(
            category="Overall Attacking Performance",
            finding_name="Strong attacking output",
            description="Team generates substantially more xG than the benchmark.",
            team_id=team_id,
            team_name=team_name
        ))

    if xgf_pct <= 10:
        findings.append(Finding(
            category="Overall Attacking Performance",
            finding_name="Very weak attacking output",
            description="Exceptionally low xG production.",
            team_id=team_id,
            team_name=team_name
        ))
    elif xgf_pct <= 20:
        findings.append(Finding(
            category="Overall Attacking Performance",
            finding_name="Weak attacking output",
            description="Team generates substantially less xG than the benchmark.",
            team_id=team_id,
            team_name=team_name
        ))
    if goals_pct <= 20:
        findings.append(Finding(
            category="Overall Attacking Performance",
            finding_name="Low Goal output",
            description="Team scores at a low rate.",
            team_id=team_id,
            team_name=team_name
        ))
    elif goals_pct >= 80:
        findings.append(Finding(
            category="Overall Attacking Performance",
            finding_name="High Goal output",
            description="Team scores at a high rate.",
            team_id=team_id,
            team_name=team_name
        ))

    if xgf_minus_goal_pct <= 20:
        findings.append(Finding(
            category="Overall Attacking Performance",
            finding_name="Goals outperforming Process",
            description="Goals above xG.",
            team_id=team_id,
            team_name=team_name
        ))
    elif xgf_minus_goal_pct >= 80:
        findings.append(Finding(
            category="Overall Attacking Performance",
            finding_name="Goals underperforming Process",
            description="Goals below xG",
            team_id=team_id,
            team_name=team_name
        ))

    return findings


# Register this module's functions
register_evaluator(evaluate_attacking_performance)
register_evidence(get_attacking_evidence)
