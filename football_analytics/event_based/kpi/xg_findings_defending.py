"""Defending findings covering defensive process, shot suppression, efficiency, and process vs outcome."""

from .xg_findings_base import Finding, register_evaluator, register_evidence
from typing import Dict, List


def get_defending_evidence(finding_name: str, team_metrics: Dict) -> str:
    """Return evidence for defending findings."""
    def get_value(metric_obj):
        return metric_obj.value if hasattr(metric_obj, 'value') else 0.0
    def get_pct(metric_obj):
        return metric_obj.percentile if hasattr(metric_obj, 'percentile') else 0.0

    evidence_map = {
        "Elite defensive process": lambda: f"xGA: {get_value(team_metrics.get('xga')):.2f} ({get_pct(team_metrics.get('xga')):.0f}th %ile)",
        "Strong defensive process": lambda: f"xGA: {get_value(team_metrics.get('xga')):.2f} ({get_pct(team_metrics.get('xga')):.0f}th %ile)",
        "Weak defensive process": lambda: f"xGA: {get_value(team_metrics.get('xga')):.2f} ({get_pct(team_metrics.get('xga')):.0f}th %ile)",
        "Very weak defensive process": lambda: f"xGA: {get_value(team_metrics.get('xga')):.2f} ({get_pct(team_metrics.get('xga')):.0f}th %ile)",
        "Strong shot suppression": lambda: f"Opponent Shots: {get_value(team_metrics.get('op_shots')):.0f} ({get_pct(team_metrics.get('op_shots')):.0f}th %ile)",
        "Poor shot suppression": lambda: f"Opponent Shots: {get_value(team_metrics.get('op_shots')):.0f} ({get_pct(team_metrics.get('op_shots')):.0f}th %ile)",
        "Defensive overperformance": lambda: f"Goals Conceded: {get_value(team_metrics.get('goals_conceded')):.0f}, xGA: {get_value(team_metrics.get('xga')):.2f}, Diff: {get_value(team_metrics.get('goals_conceded')) - get_value(team_metrics.get('xga')):.2f}",
        "Defensive underperformance": lambda: f"Goals Conceded: {get_value(team_metrics.get('goals_conceded')):.0f}, xGA: {get_value(team_metrics.get('xga')):.2f}, Diff: {get_value(team_metrics.get('goals_conceded')) - get_value(team_metrics.get('xga')):.2f}",
        "Attack outperforming process": lambda: f"Goals: {get_value(team_metrics.get('goals')):.0f}, xGF: {get_value(team_metrics.get('xgf')):.2f}, +{get_value(team_metrics.get('goals')) - get_value(team_metrics.get('xgf')):.2f}",
        "Attack underperforming process": lambda: f"Goals: {get_value(team_metrics.get('goals')):.0f}, xGF: {get_value(team_metrics.get('xgf')):.2f}, {get_value(team_metrics.get('goals')) - get_value(team_metrics.get('xgf')):.2f}",
        "Defence outperforming process": lambda: f"Conceded: {get_value(team_metrics.get('goals_conceded')):.0f}, xGA: {get_value(team_metrics.get('xga')):.2f}, {get_value(team_metrics.get('goals_conceded')) - get_value(team_metrics.get('xga')):.2f}",
        "Defence underperforming process": lambda: f"Conceded: {get_value(team_metrics.get('goals_conceded')):.0f}, xGA: {get_value(team_metrics.get('xga')):.2f}, +{get_value(team_metrics.get('goals_conceded')) - get_value(team_metrics.get('xga')):.2f}",
    }

    if finding_name in evidence_map:
        try:
            return evidence_map[finding_name]()
        except:
            return None
    return None


def evaluate_defending(team_id: int, team_name: str, team_metrics: Dict,
                       get_value, get_pct) -> List[Finding]:
    """Evaluate all defensive findings."""
    findings = []
    xga_pct = get_pct(team_metrics.get('xga'))
    op_shots_pct = get_pct(team_metrics.get('op_shots'))
    goals_conceded_val = get_value(team_metrics.get('goals_conceded'))
    xga_val = get_value(team_metrics.get('xga'))
    goals_val = get_value(team_metrics.get('goals'))
    xgf_val = get_value(team_metrics.get('xgf'))

    # ===== DEFENSIVE PROCESS =====
    if xga_pct <= 10:
        findings.append(Finding(
            category="Defending",
            finding_name="Elite defensive process",
            description="Exceptionally low xGA.",
            team_id=team_id,
            team_name=team_name
        ))
    elif xga_pct <= 20:
        findings.append(Finding(
            category="Defending",
            finding_name="Strong defensive process",
            description="Team restricts opponents to low xG.",
            team_id=team_id,
            team_name=team_name
        ))

    if xga_pct >= 90:
        findings.append(Finding(
            category="Defending",
            finding_name="Very weak defensive process",
            description="Exceptionally high xGA.",
            team_id=team_id,
            team_name=team_name
        ))
    elif xga_pct >= 80:
        findings.append(Finding(
            category="Defending",
            finding_name="Weak defensive process",
            description="Opponents generate substantial xG.",
            team_id=team_id,
            team_name=team_name
        ))

    # ===== DEFENSIVE SHOT SUPPRESSION =====
    if op_shots_pct <= 20:
        findings.append(Finding(
            category="Defensive Shot Suppression",
            finding_name="Strong shot suppression",
            description="Opponents take relatively few shots.",
            team_id=team_id,
            team_name=team_name
        ))
    if op_shots_pct >= 80:
        findings.append(Finding(
            category="Defensive Shot Suppression",
            finding_name="Poor shot suppression",
            description="Opponents generate high shot volume.",
            team_id=team_id,
            team_name=team_name
        ))

    # ===== DEFENSIVE EFFICIENCY =====
    conceded_diff = goals_conceded_val - xga_val
    if conceded_diff <= -1.0:
        findings.append(Finding(
            category="Defensive Efficiency",
            finding_name="Defensive overperformance",
            description="Fewer goals conceded than expected.",
            team_id=team_id,
            team_name=team_name
        ))
    if conceded_diff >= 1.0:
        findings.append(Finding(
            category="Defensive Efficiency",
            finding_name="Defensive underperformance",
            description="More goals conceded than expected.",
            team_id=team_id,
            team_name=team_name
        ))

    # ===== PROCESS VS OUTCOME =====
    goal_diff = goals_val - xgf_val
    if goal_diff >= 1.5:
        findings.append(Finding(
            category="Process vs Outcome",
            finding_name="Attack outperforming process",
            description="Scoring output is substantially above the underlying xG process.",
            team_id=team_id,
            team_name=team_name
        ))
    if goal_diff <= -1.5:
        findings.append(Finding(
            category="Process vs Outcome",
            finding_name="Attack underperforming process",
            description="Scoring output is substantially below the underlying xG process.",
            team_id=team_id,
            team_name=team_name
        ))

    if conceded_diff <= -1.5:
        findings.append(Finding(
            category="Process vs Outcome",
            finding_name="Defence outperforming process",
            description="Goals conceded are substantially below xGA.",
            team_id=team_id,
            team_name=team_name
        ))
    if conceded_diff >= 1.5:
        findings.append(Finding(
            category="Process vs Outcome",
            finding_name="Defence underperforming process",
            description="Goals conceded are substantially above xGA.",
            team_id=team_id,
            team_name=team_name
        ))

    return findings

# Register this module's functions
register_evaluator(evaluate_defending)
register_evidence(get_defending_evidence)
