"""
XGPlayerPlugin
--------------
Player-level Expected Goals KPI plugin.

Derived indicators (all non-obvious — must pass the scout test):
    1. Finishing differential (Goals − xG) with sample-size awareness
    2. xG per shot — positioning and movement intelligence
    3. Post-shot vs pre-shot xG gap — technique separated from position
    4. xG involvement — own xG + xG of shots created for others
    5. xG consistency — standard deviation alongside mean
    6. xG vs opponent quality splits — top/mid/bottom tier breakdown
    7. xG under pressure / game state

The scout test: would a good scout see this across 5–6 games of watching?
If yes, it's not a primary KPI. Every indicator here answers 'no'.
"""

import pandas as pd
import numpy as np
from kpi.base_plugin import BaseKPIPlugin, KPIResult, Indicator


class XGPlayerPlugin(BaseKPIPlugin):

    plugin_id = 'xg_player'
    display_name = 'Expected Goals — Player'
    required_fields = ['player_stats', 'league_benchmarks']
    min_sample_size = 8                     # more games needed for player-level signal
    min_shots_for_finishing = 30            # shots needed before finishing differential is meaningful
    tags = ['player', 'attacking', 'core', 'recruitment']

    # Interpretation thresholds
    FINISHING_DIFF_MEANINGFUL = 30          # shots needed
    FINISHING_DIFF_HIGH = 2.5              # goals above xG = strong signal
    XG_PER_SHOT_ELITE = 0.14
    XG_PER_SHOT_GOOD = 0.11
    XG_PER_SHOT_POOR = 0.07
    TECHNIQUE_VALUE_HIGH = 0.02            # post vs pre shot xG gap
    CONSISTENCY_LOW_STD = 0.08            # low std = consistent generator

    def can_run(self, dataset) -> bool:
        if not self._has_required_fields(dataset):
            return False
        if dataset.player_stats is None or dataset.player_stats.empty:
            return False
        return True

    def calculate(self, dataset) -> KPIResult:
        try:
            return self._calculate(dataset)
        except Exception as e:
            return self._build_low_confidence_result(str(e))

    def _calculate(self, dataset) -> KPIResult:
        stats = dataset.player_stats
        benchmarks = dataset.league_benchmarks
        recipe = dataset.recipe
        n_games = len(stats['match_id'].unique()) if 'match_id' in stats.columns else 0

        indicators = []

        # --- 1. Finishing Differential ---
        ind = self._finishing_differential(stats, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        # --- 2. xG Per Shot ---
        ind = self._xg_per_shot(stats, benchmarks, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        # --- 3. Post-Shot vs Pre-Shot xG ---
        ind = self._technique_value(stats, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        # --- 4. xG Involvement ---
        ind = self._xg_involvement(stats, benchmarks, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        # --- 5. xG Consistency ---
        ind = self._xg_consistency(stats, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        # --- 6. xG vs Opponent Quality ---
        ind = self._xg_opponent_splits(stats, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        # --- 7. xG Under Pressure ---
        ind = self._xg_under_pressure(stats, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        findings = self._generate_findings(indicators, recipe, n_games, stats)

        return KPIResult(
            plugin_id=self.plugin_id,
            display_name=self.display_name,
            indicators=indicators,
            findings=findings,
            confidence=recipe.confidence_score,
            confidence_level=recipe.confidence_level,
            flags=recipe.flags,
            required_sample_met=self._check_sample_size(n_games),
            tags=self.tags,
            metadata={
                'n_games': n_games,
                'player_id': stats['player_id'].iloc[0] if 'player_id' in stats.columns else None,
            }
        )

    # ---------------------------------------------------------------------------
    # Indicator calculators
    # ---------------------------------------------------------------------------

    def _finishing_differential(
        self, stats: pd.DataFrame, confidence: float
    ) -> Indicator | None:
        """
        Goals minus xG across all shots.
        Non-obvious: separates finishing skill from chance quality.
        Requires minimum shot threshold before result is surfaced.

        TODO: implement once player_stats schema is defined.
        Requires: 'goals', 'xg', 'shot_id' columns.
        """
        # STUB
        # total_shots = stats['shot_id'].nunique()
        # goals = stats['goals'].sum()
        # xg = stats['xg'].sum()
        # diff = goals - xg
        # sample_sufficient = total_shots >= self.FINISHING_DIFF_MEANINGFUL
        return None

    def _xg_per_shot(
        self, stats: pd.DataFrame, benchmarks: pd.DataFrame, confidence: float
    ) -> Indicator | None:
        """
        xG divided by total shots.
        Non-obvious: reveals movement quality and position intelligence
        independent of finishing ability.

        TODO: implement once player_stats schema is defined.
        Requires: 'xg', 'shot_id' columns.
        """
        # STUB
        # xg_per_shot = stats['xg'].sum() / stats['shot_id'].nunique()
        # percentile = self._percentile_rank(xg_per_shot, benchmarks['xg_per_shot'].tolist())
        return None

    def _technique_value(
        self, stats: pd.DataFrame, confidence: float
    ) -> Indicator | None:
        """
        Post-shot xG minus pre-shot xG.
        Non-obvious: isolates technique (placement, power, direction)
        from positional quality. A positive value means the player
        adds value through how they finish, not just where from.

        TODO: implement once player_stats schema has post_shot_xg.
        Requires: 'xg' (pre-shot), 'post_shot_xg' columns.
        """
        # STUB
        # pre = stats['xg'].sum()
        # post = stats['post_shot_xg'].sum()
        # technique_value = post - pre
        return None

    def _xg_involvement(
        self, stats: pd.DataFrame, benchmarks: pd.DataFrame, confidence: float
    ) -> Indicator | None:
        """
        Own xG plus xG generated on shots assisted.
        Non-obvious: captures total attacking contribution —
        separates pure finishers from creators from complete attackers.

        TODO: implement once player_stats schema is defined.
        Requires: 'xg' (own shots), 'xa' (expected assists) columns.
        """
        # STUB
        # own_xg_per90 = ...
        # xa_per90 = ...
        # involvement = own_xg_per90 + xa_per90
        return None

    def _xg_consistency(
        self, stats: pd.DataFrame, confidence: float
    ) -> Indicator | None:
        """
        Standard deviation of per-game xG alongside the mean.
        Non-obvious: two players with identical xG means can be
        completely different propositions — one consistent, one volatile.

        TODO: implement once player_stats schema is defined.
        Requires: per-game 'xg' column with 'match_id'.
        """
        # STUB
        # per_game_xg = stats.groupby('match_id')['xg'].sum()
        # mean_xg = per_game_xg.mean()
        # std_xg = per_game_xg.std()
        return None

    def _xg_opponent_splits(
        self, stats: pd.DataFrame, confidence: float
    ) -> Indicator | None:
        """
        xG per shot split by opponent tier (top / mid / bottom third).
        Non-obvious: reveals whether a player's output holds up
        against better defences — critical for recruitment targeting.

        TODO: implement once opponent quality index is available.
        Requires: 'opponent_tier' column ('top' | 'mid' | 'bottom').
        """
        # STUB
        # top_xg_per_shot = stats[stats['opponent_tier'] == 'top']['xg'].mean()
        # mid_xg_per_shot = ...
        # bot_xg_per_shot = ...
        return None

    def _xg_under_pressure(
        self, stats: pd.DataFrame, confidence: float
    ) -> Indicator | None:
        """
        xG per shot when team is winning / drawing / losing.
        Non-obvious: closest data proxy for big-game mentality.
        Some players' output disappears in high-leverage situations.

        TODO: implement once match game state data is available.
        Requires: 'game_state' column ('winning' | 'drawing' | 'losing').
        """
        # STUB
        return None

    # ---------------------------------------------------------------------------
    # Findings generator
    # ---------------------------------------------------------------------------

    def _generate_findings(
        self,
        indicators: list[Indicator],
        recipe,
        n_games: int,
        stats: pd.DataFrame,
    ) -> list[str]:
        """
        Generate narrative findings from calculated indicators.

        Follows the platform philosophy:
            Lead with insight. Use indicators as evidence.
            The finding should tell a recruitment team what to do next.

        TODO: implement as indicators are built out.
        """
        findings = []

        if not self._check_sample_size(n_games):
            findings.append(
                f"Small sample — {n_games} games available. "
                f"Player-level xG requires 8+ games for reliable signal. "
                f"Treat all indicators as directional only."
            )

        # TODO: implement indicator-driven findings
        # Example pattern once finishing_differential is built:
        #
        # fin = self._get_indicator(indicators, 'finishing_differential')
        # xg_shot = self._get_indicator(indicators, 'xg_per_shot')
        #
        # if fin and xg_shot:
        #     if fin.value > 2.0 and xg_shot.percentile > 70:
        #         findings.append(
        #             "Elite profile — generating high-quality positions AND "
        #             "consistently converting above expectation. "
        #             "Sustained over two or more seasons this warrants a premium valuation."
        #         )
        #     elif fin.value < -2.0 and xg_shot.percentile > 70:
        #         findings.append(
        #             "Undervalued profile — movement and positioning rank in the "
        #             "top 30% of the position group but finishing is suppressing "
        #             "goal output. Positive regression expected."
        #         )

        return findings

    def _get_indicator(self, indicators: list[Indicator], id: str) -> Indicator | None:
        return next((i for i in indicators if i.id == id), None)
