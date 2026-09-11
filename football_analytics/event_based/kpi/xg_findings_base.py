"""
XG Findings Base: Core classes and registry for findings evaluation.

Contains:
- Finding dataclass
- Registry for finding evaluators and evidence functions
- Registration functions for modules to register themselves
- Key mapping helpers for coordinate-based metric names
"""

from typing import Dict, Callable, List, Optional, Any
from dataclasses import dataclass


def create_percentile_findings(value: float, upper_threshold: float, lower_threshold: float,
                                finding_name: str, category: str, team_id: int, team_name: str) -> List['Finding']:
    """
    Create findings based on percentile thresholds.

    Args:
        value: Percentile value (0-100)
        upper_threshold: Threshold for "High" finding (e.g., 80)
        lower_threshold: Threshold for "Low" finding (e.g., 20)
        finding_name: Base finding name (e.g., "attacking output")
        category: Finding category
        team_id: Team ID
        team_name: Team name

    Returns:
        List of Finding objects if thresholds are met, empty list otherwise
    """
    findings = []

    if value >= upper_threshold:
        findings.append(Finding(
            category=category,
            finding_name=f"High {finding_name}",
            team_id=team_id,
            team_name=team_name
        ))
    elif value <= lower_threshold:
        findings.append(Finding(
            category=category,
            finding_name=f"Low {finding_name}",
            team_id=team_id,
            team_name=team_name
        ))

    return findings


@dataclass
class Finding:
    """Represents a triggered finding."""
    category: str
    finding_name: str
    team_id: int
    team_name: str


# Global registries
_evaluator_registry: List[Callable] = []
_evidence_registry: List[Callable] = []


def register_evaluator(evaluator_func: Callable) -> None:
    """
    Register a finding evaluator function.

    Args:
        evaluator_func: A function with signature:
            evaluate_*(team_id, team_name, team_metrics, get_value, get_pct) -> List[Finding]
    """
    _evaluator_registry.append(evaluator_func)


def register_evidence(evidence_func: Callable) -> None:
    """
    Register an evidence function.

    Args:
        evidence_func: A function with signature:
            get_*_evidence(finding_name, team_metrics) -> str
    """
    _evidence_registry.append(evidence_func)


def get_finding_evidence(finding_name: str, team_metrics: Dict) -> str:
    """
    Return relevant metric evidence for a finding.

    Uses registered evidence functions to find supporting data.
    """
    for evidence_func in _evidence_registry:
        try:
            evidence = evidence_func(finding_name, team_metrics)
            if evidence:
                return evidence
        except Exception:
            continue

    return None


def get_evaluators() -> List[Callable]:
    """Get all registered evaluators."""
    return _evaluator_registry.copy()


def get_evidence_functions() -> List[Callable]:
    """Get all registered evidence functions."""
    return _evidence_registry.copy()


# Mapping from legacy metric names to coordinate-based keys
LEGACY_TO_COORDINATE = {
    # XG metrics (for attacking team)
    'xgf': 'xg_for_total',
    'xgf_penalty': 'xg_for_penalty',
    'xgf_open_play': 'xg_for_open_play',
    'xgf_set_piece': 'xg_for_set_piece_total',
    'xgf_open_play_inbox': 'xg_for_inbox',
    'xgf_open_play_outbox': 'xg_for_outbox',
    # Shot metrics (for attacking team)
    'shots': 'shot_for_total',
    'shots_penalty': 'shot_for_penalty',
    'shots_open_play': 'shot_for_open_play',
    'shots_open_play_inbox': 'shot_for_inbox',
    'shots_open_play_outbox': 'shot_for_outbox',
    'shots_corner': 'shot_for_set_piece_corner',
    'shots_free_kick': 'shot_for_set_piece_free_kick',
    'shots_headers': 'shot_for_header',
    'shots_on_target': 'shot_target_for_total',
    'one_on_one_shots': 'shot_for_one_on_one',
}


def get_metric(team_metrics: Dict, legacy_key: str) -> Optional[Any]:
    """
    Get a metric by legacy key, automatically converting to coordinate-based key.

    Args:
        team_metrics: Dictionary of aggregated metrics with coordinate-based keys
        legacy_key: Legacy metric name (e.g., 'xgf', 'shots')

    Returns:
        Metric object or None if not found
    """
    # Try coordinate-based key first
    coord_key = LEGACY_TO_COORDINATE.get(legacy_key, legacy_key)
    if coord_key in team_metrics:
        return team_metrics[coord_key]

    # Fallback to direct lookup
    if legacy_key in team_metrics:
        return team_metrics[legacy_key]

    return None
