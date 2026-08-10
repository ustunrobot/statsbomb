"""
Base metric class and shared utilities.

All metric modules inherit from BaseMetric and implement compute()
to return a dictionary of measurements.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import dict
from utils.pitch_zones import BUILDUP_X_THRESHOLD, PROGRESSIVE_PASS_THRESHOLD


class BaseMetric(ABC):
    """
    Abstract base class for all football metrics.

    Provides common filtering, normalization, and utility methods.
    Each subclass implements compute() to return a flat dict of metrics.
    """

    def __init__(self, events_df: pd.DataFrame, team: str, match_id: str = None):
        """
        Initialize metric calculator.

        Args:
            events_df: Complete match events DataFrame
            team: Team name to analyze
            match_id: Match identifier (optional, inferred from events if not provided)

        Football context:
            events_df should contain all events from one match,
            including both teams. The team parameter filters to
            this team's possession only.
        """
        self.events_df = events_df
        self.team = team
        self.match_id = match_id or events_df['match_id'].iloc[0] if len(events_df) > 0 else None

    @abstractmethod
    def compute(self) -> dict:
        """
        Compute all metrics for this team in this match.

        Must return a flat dictionary with keys like:
        - Metric name (e.g., 'possession_pct', 'pass_completion')
        - Value: float, int, list, or dict

        Each metric key should be prefixed with a module abbreviation
        for clarity (e.g., 'pzdi_def_pct' for possession zone distribution).

        Returns:
            Dict[str, float | int | list | dict]
        """
        pass

    def filter_team_events(self) -> pd.DataFrame:
        """
        Filter events to possession sequences of the team.

        Returns:
            DataFrame of events where team is the possessing team.

        Football interpretation:
            Possession events are passes, carries, dribbles, and
            events initiated by the team when they control the ball.
        """
        return self.events_df[self.events_df['team'] == self.team].copy()

    def get_buildup_events(self) -> pd.DataFrame:
        """
        Filter to buildup phase (defensive third) for the team.

        Returns:
            DataFrame of team events with x < BUILDUP_X_THRESHOLD.

        Football interpretation:
            Buildup is the defensive/middle phase where a team
            constructs attacking play from their defensive area.
            Low-risk passing patterns dominate here.
        """
        team_events = self.filter_team_events()
        buildup = team_events[team_events['x'] < BUILDUP_X_THRESHOLD].copy()
        return buildup

    def normalize_per_90(self, value: float, minutes: float) -> float:
        """
        Normalize a statistic to per-90-minute basis.

        Args:
            value: Raw count or sum
            minutes: Total minutes played

        Returns:
            Normalized value per 90 minutes

        Football interpretation:
            Per-90 normalization allows fair comparison across
            different match durations and player minutes.
        """
        if minutes == 0:
            return 0.0
        return (value / minutes) * 90.0

    def get_match_duration(self) -> float:
        """
        Extract match duration in minutes.

        Returns:
            Float: total minutes of match.
        """
        max_minute = self.events_df['minute'].max()
        return float(max_minute) if pd.notna(max_minute) else 90.0
