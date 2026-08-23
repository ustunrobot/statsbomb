"""
Type definitions for football analytics.

Provides dataclasses and type hints for type-safe data handling.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional



@dataclass
class TeamMetrics:
    """
    Metrics and statistics for a team.

    Attributes:
        n_events: Total number of events
        n_matches: Total number of matches
        n_metrics: Total number of metrics
        style_of_play: Dict of style of play metrics (sop_* keys)
        buildup_stats: Dict of buildup statistics (aggregated from buildups)
        buildups: List of individual buildup sequence dicts
        shape: Dict of shape data
        other_metrics: Additional metrics (flexible for future expansion)
    """
    n_events: int = 0
    n_matches: int = 0
    n_metrics: int = 0
    style_of_play: Dict[str, Any] = field(default_factory=dict)
    buildup_stats: Dict[str, Any] = field(default_factory=dict)
    buildups: List[Dict[str, Any]] = field(default_factory=list)
    shape: Dict = field(default_factory=dict)
    other_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TeamStats:
    """
    Statistics for a team.

    Attributes:
        team: Team name
        metrics: TeamMetrics object containing all team metrics
    """
    team: str
    all: TeamMetrics = field(default_factory=TeamMetrics)
    last_season: TeamMetrics = field(default_factory=TeamMetrics)
    this_season: TeamMetrics = field(default_factory=TeamMetrics)
    last_5: TeamMetrics = field(default_factory=TeamMetrics) 
    last_game: TeamMetrics = field(default_factory=TeamMetrics) 

    