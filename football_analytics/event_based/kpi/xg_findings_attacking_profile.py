"""Attacking Profile findings."""

from .xg_findings_base import Finding, register_evaluator, register_evidence, get_metric
from typing import Dict, List


def get_attacking_profile_evidence(finding_name: str, team_metrics: Dict) -> str:
    """Return evidence for attacking profile findings."""
    def get_value(metric_obj):
        return metric_obj.value if hasattr(metric_obj, 'value') else 0.0
    def get_pct(metric_obj):
        return metric_obj.percentile if hasattr(metric_obj, 'percentile') else 0.0

    xgf_set_piece_ratio = get_metric(team_metrics, 'xgf_set_piece_ratio') or team_metrics.get('xgf_set_piece_ratio')
    xgf_open_play_ratio = get_metric(team_metrics, 'xgf_open_play_ratio') or team_metrics.get('xgf_open_play_ratio')

    evidence_map = {
        "Open-play dominant attack": lambda: f"Open Play xGF Ratio: {get_value(xgf_open_play_ratio):.1%}",
        "Set-piece dependent attack": lambda: f"Set Piece xGF Ratio: {get_value(xgf_set_piece_ratio):.1%}",
        "Low set-piece reliance": lambda: f"Set Piece xGF Ratio: {get_value(xgf_set_piece_ratio):.1%}",
        "High set-piece xgf ratio": lambda: f"Set Piece xGF Ratio: {get_value(xgf_set_piece_ratio):.1%} ({get_pct(xgf_set_piece_ratio):.0f}th %ile)",
        "Low set-piece xgf ratio": lambda: f"Set Piece xGF Ratio: {get_value(xgf_set_piece_ratio):.1%} ({get_pct(xgf_set_piece_ratio):.0f}th %ile)",
        "High open play xgf ratio": lambda: f"Open Play xGF Ratio: {get_value(xgf_open_play_ratio):.1%} ({get_pct(xgf_open_play_ratio):.0f}th %ile)",
        "Low open play xgf ratio": lambda: f"Open Play xGF Ratio: {get_value(xgf_open_play_ratio):.1%} ({get_pct(xgf_open_play_ratio):.0f}th %ile)",
    }

    if finding_name in evidence_map:
        try:
            return evidence_map[finding_name]()
        except:
            return None
    return None


def evaluate_attacking_profile(team_id: int, team_name: str, team_metrics: Dict,
                               get_value, get_pct) -> List[Finding]:
    """Evaluate attacking profile findings."""
    findings = []

    xgf_set_piece_ratio_pct = get_pct(get_metric(team_metrics, 'xgf_set_piece_ratio') or team_metrics.get('xgf_set_piece_ratio'))
    xgf_open_play_ratio_pct = get_pct(get_metric(team_metrics, 'xgf_open_play_ratio') or team_metrics.get('xgf_open_play_ratio'))

    # Set piece xGF ratio
    if xgf_set_piece_ratio_pct >= 80:
        findings.append(Finding(
            category="Attacking Profile",
            finding_name="High set-piece xgf ratio",
            description="Large proportion of attacking xGF comes from set pieces.",
            team_id=team_id,
            team_name=team_name
        ))
    if xgf_set_piece_ratio_pct <= 20:
        findings.append(Finding(
            category="Attacking Profile",
            finding_name="Low set-piece xgf ratio",
            description="Small proportion of attacking xGF comes from set pieces.",
            team_id=team_id,
            team_name=team_name
        ))

    # Open play xGF ratio
    if xgf_open_play_ratio_pct >= 80:
        findings.append(Finding(
            category="Attacking Profile",
            finding_name="High open play xgf ratio",
            description="Large proportion of attacking xGF comes from open play.",
            team_id=team_id,
            team_name=team_name
        ))
    if xgf_open_play_ratio_pct <= 20:
        findings.append(Finding(
            category="Attacking Profile",
            finding_name="Low open play xgf ratio",
            description="Small proportion of attacking xGF comes from open play.",
            team_id=team_id,
            team_name=team_name
        ))

    return findings

# Register this module's functions
register_evaluator(evaluate_attacking_profile)
register_evidence(get_attacking_profile_evidence)
