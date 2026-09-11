"""Chance Creation findings."""

from typing import Dict, List
from .xg_findings_base import Finding, register_evaluator, register_evidence, get_metric, create_percentile_findings


def get_chance_creation_evidence(finding_name: str, team_metrics: Dict) -> str:
    """Return evidence for chance creation findings."""
    def get_value(metric_obj):
        return metric_obj.value if hasattr(metric_obj, 'value') else 0.0
    def get_pct(metric_obj):
        return metric_obj.percentile if hasattr(metric_obj, 'percentile') else 0.0

    shots = get_metric(team_metrics, 'shots') or team_metrics.get('shots')
    shots_open_play = get_metric(team_metrics, 'shots_open_play') or team_metrics.get('shots_open_play')
    shots_penalty = get_metric(team_metrics, 'shots_penalty') or team_metrics.get('shots_penalty')
    shots_free_kick = get_metric(team_metrics, 'shots_free_kick') or team_metrics.get('shots_free_kick')
    one_on_one_shots = get_metric(team_metrics, 'one_on_one_shots') or team_metrics.get('one_on_one_shots')
    shots_outbox_per_shots = get_metric(team_metrics, 'shots_outbox_per_shots') or team_metrics.get('shots_outbox_per_shots')
    xgf_open_play_outbox_per_xgf = get_metric(team_metrics, 'xgf_open_play_outbox_per_xgf') or team_metrics.get('xgf_open_play_outbox_per_xgf')

    evidence_map = {
        "High shooting volume": lambda: f"Shots: {get_value(shots):.0f} ({get_pct(shots):.0f}th %ile)",
        "Low shooting volume": lambda: f"Shots: {get_value(shots):.0f} ({get_pct(shots):.0f}th %ile)",
        "High open play shooting volume": lambda: f"Open Play Shots: {get_value(shots_open_play):.0f} ({get_pct(shots_open_play):.0f}th %ile)",
        "Low open play shooting volume": lambda: f"Open Play Shots: {get_value(shots_open_play):.0f} ({get_pct(shots_open_play):.0f}th %ile)",
        "High penalty shooting volume": lambda: f"Penalty Shots: {get_value(shots_penalty):.0f} ({get_pct(shots_penalty):.0f}th %ile)",
        "Low penalty shooting volume": lambda: f"Penalty Shots: {get_value(shots_penalty):.0f} ({get_pct(shots_penalty):.0f}th %ile)",
        "High free kick shooting volume": lambda: f"Free Kick Shots: {get_value(shots_free_kick):.0f} ({get_pct(shots_free_kick):.0f}th %ile)",
        "Low free kick shooting volume": lambda: f"Free Kick Shots: {get_value(shots_free_kick):.0f} ({get_pct(shots_free_kick):.0f}th %ile)",
        "High one-on-one shooting volume": lambda: f"One-on-One Shots: {get_value(one_on_one_shots):.0f} ({get_pct(one_on_one_shots):.0f}th %ile)",
        "Low one-on-one shooting volume": lambda: f"One-on-One Shots: {get_value(one_on_one_shots):.0f} ({get_pct(one_on_one_shots):.0f}th %ile)",
        "High outbox shot ratio": lambda: f"Outbox Shots Ratio: {get_value(shots_outbox_per_shots):.1%} ({get_pct(shots_outbox_per_shots):.0f}th %ile)",
        "Low outbox shot ratio": lambda: f"Outbox Shots Ratio: {get_value(shots_outbox_per_shots):.1%} ({get_pct(shots_outbox_per_shots):.0f}th %ile)",
        "High outbox xgf ratio": lambda: f"Outbox xGF Ratio: {get_value(xgf_open_play_outbox_per_xgf):.1%} ({get_pct(xgf_open_play_outbox_per_xgf):.0f}th %ile)",
        "Low outbox xgf ratio": lambda: f"Outbox xGF Ratio: {get_value(xgf_open_play_outbox_per_xgf):.1%} ({get_pct(xgf_open_play_outbox_per_xgf):.0f}th %ile)",
    }

    if finding_name in evidence_map:
        try:
            return evidence_map[finding_name]()
        except:
            return None
    return None


def evaluate_chance_creation(team_id: int, team_name: str, team_metrics: Dict,
                             get_value, get_pct) -> List[Finding]:
    """Evaluate chance creation findings."""
    findings = []
    category = "Chance Creation"

    shots_pct = get_pct(get_metric(team_metrics, 'shots') or team_metrics.get('shots'))
    shots_open_play_pct = get_pct(get_metric(team_metrics, 'shots_open_play') or team_metrics.get('shots_open_play'))
    shots_penalty_pct = get_pct(get_metric(team_metrics, 'shots_penalty') or team_metrics.get('shots_penalty'))
    shots_free_kick_pct = get_pct(get_metric(team_metrics, 'shots_free_kick') or team_metrics.get('shots_free_kick'))
    one_on_one_shots_pct = get_pct(get_metric(team_metrics, 'one_on_one_shots') or team_metrics.get('one_on_one_shots'))
    shots_outbox_per_shots_pct = get_pct(get_metric(team_metrics, 'shots_outbox_per_shots') or team_metrics.get('shots_outbox_per_shots'))
    xgf_open_play_outbox_per_xgf_pct = get_pct(get_metric(team_metrics, 'xgf_open_play_outbox_per_xgf') or team_metrics.get('xgf_open_play_outbox_per_xgf'))

    findings.extend(create_percentile_findings(shots_pct, 80, 20, "shooting volume", category, team_id, team_name))
    findings.extend(create_percentile_findings(shots_open_play_pct, 80, 20, "open play shooting volume", category, team_id, team_name))
    findings.extend(create_percentile_findings(shots_penalty_pct, 80, 20, "penalty shooting volume", category, team_id, team_name))
    findings.extend(create_percentile_findings(shots_free_kick_pct, 80, 20, "free kick shooting volume", category, team_id, team_name))
    findings.extend(create_percentile_findings(one_on_one_shots_pct, 80, 20, "one-on-one shooting volume", category, team_id, team_name))
    findings.extend(create_percentile_findings(shots_outbox_per_shots_pct, 80, 20, "outbox shot ratio", category, team_id, team_name))
    findings.extend(create_percentile_findings(xgf_open_play_outbox_per_xgf_pct, 80, 20, "outbox xgf ratio", category, team_id, team_name))

    return findings


# Register this module's functions
register_evaluator(evaluate_chance_creation)
register_evidence(get_chance_creation_evidence)
