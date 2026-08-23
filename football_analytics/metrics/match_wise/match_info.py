"""
Match-wise metrics — match result and outcome information.

Calculates match-level metrics like points earned, goals scored/conceded.
Useful for understanding match outcome and performance context.
"""

import pandas as pd
from metrics.base import BaseMetric


class MatchInfo(BaseMetric):
    """
    Analyze match result and outcome metrics.

    Metrics computed:
    1. Total Points (3 for win, 1 for draw)
    2. Goals Scored
    3. Goals Conceded
    4. Match Result (W/D/L)
    """

    def compute(self) -> dict:
        """
        Compute all match info metrics.

        Returns:
            Flat dictionary with keys prefixed 'mi_' (match info).
        """
        result = {}

        result.update(self._match_result_and_points())
        result.update(self._goals_scored_conceded())

        return result

    def _match_result_and_points(self) -> dict:
        """
        Calculate points earned based on match result (W/D/L).

        3 points for a win, 1 point for a draw, 0 for a loss.

        Returns:
            Dict with keys: mi_points, mi_result
        """
        goals_scored = self._count_goals_for_team(self.team)
        goals_conceded = self._count_goals_for_team_opponent()

        if goals_scored > goals_conceded:
            points = 3
            result_code = 'W'
        elif goals_scored == goals_conceded:
            points = 1
            result_code = 'D'
        else:
            points = 0
            result_code = 'L'

        return {
            'mi_points': int(points),
            'mi_result': result_code,
        }

    def _goals_scored_conceded(self) -> dict:
        """
        Count goals scored by team and conceded.

        Uses shot events to count goals. Assumes all shots in the data
        represent goal-scoring attempts/outcomes.

        Returns:
            Dict with keys: mi_goals_scored, mi_goals_conceded
        """
        goals_scored = self._count_goals_for_team(self.team)
        goals_conceded = self._count_goals_for_team_opponent()

        return {
            'mi_goals_scored': int(goals_scored),
            'mi_goals_conceded': int(goals_conceded),
        }

    def _count_goals_for_team(self, team: str) -> int:
        """
        Count goals scored by a specific team.

        Counts shot events by the team (proxy for goals).
        In full StatsBomb data, would filter for successful shots.

        Args:
            team: Team name

        Returns:
            Number of goals (shots) by the team
        """
        team_shots = self.events_df[
            (self.events_df['team'] == team) &
            (self.events_df['type_name'] == 'Shot')
        ]
        return len(team_shots)

    def _count_goals_for_team_opponent(self) -> int:
        """
        Count goals conceded (goals by opposing team).

        Returns:
            Number of goals conceded
        """
        # Get all teams in this match
        all_teams = self.events_df['team'].dropna().unique()
        opponent_teams = [t for t in all_teams if t != self.team]

        total_conceded = 0
        for opp_team in opponent_teams:
            total_conceded += self._count_goals_for_team(opp_team)

        return total_conceded
