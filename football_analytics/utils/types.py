"""
Type definitions for football analytics.

Provides dataclasses and type hints for type-safe data handling.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class TeamStats:
    """
    Statistics for a team in a single match.

    Attributes:
        team: Team name
        match_id: Unique match identifier
        n_events: Total number of events in the match
        style_of_play: Dict of style of play metrics (sop_* keys)
        buildup_stats: Dict of buildup statistics (aggregated from buildups)
        buildups: List of individual buildup sequence dicts
        other_metrics: Additional metrics (flexible for future expansion)
    """
    team: str
    n_events: int
    n_matches: int
    n_metrics: int
    style_of_play: Dict[str, Any] = field(default_factory=dict)
    buildup_stats: Dict[str, Any] = field(default_factory=dict)
    buildups: List[Dict[str, Any]] = field(default_factory=list)
    shape: Dict = field(default_factory=dict)
    other_metrics: Dict[str, Any] = field(default_factory=dict)

    