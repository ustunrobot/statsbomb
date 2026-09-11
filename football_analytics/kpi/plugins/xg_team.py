"""
XGTeamPlugin
------------
Team-level Expected Goals KPI plugin.

Derived indicators (all non-obvious by design — see platform philosophy):
    1. xG Table vs Actual Table (position divergence)
    2. Finishing divergence — goals vs xG with regression flag
    3. xG profile quadrant — attack vs defence positioning
    4. xG source breakdown — open play / set piece / penalty split
    5. xG per shot — shot selection quality (attack and defence)
    6. Opponent-adjusted xGD — strength-of-schedule corrected
    7. xG under pressure — game state splits

Each indicator includes:
    - Raw value
    - Formatted display string
    - Human-readable interpretation
    - Confidence score (from DataRecipe)
    - League percentile rank where applicable

Findings are generated last, once all indicators are calculated,
so they can reference multiple indicators in combination.
"""

import pandas as pd
from kpi.base_plugin import BaseKPIPlugin, KPIResult, Indicator


class XGTeamPlugin(BaseKPIPlugin):

    plugin_id = 'xg_team'
    display_name = 'Expected Goals — Team'
    required_fields = ['team_stats', 'league_benchmarks']
    min_sample_size = 6
    tags = ['team', 'attacking', 'defensive', 'core']

    # Thresholds for interpretation labels
    POSITION_DIVERGENCE_THRESHOLD = 2      # places
    FINISHING_DIVERGENCE_THRESHOLD = 1.5   # goals
    REGRESSION_RISK_THRESHOLD = 3.0        # goals overperformance
    XG_PER_SHOT_HIGH = 0.12
    XG_PER_SHOT_LOW = 0.08

    def can_run(self, dataset) -> bool:
        if not self._has_required_fields(dataset):
            return False
        if dataset.team_stats is None or dataset.team_stats.empty:
            return False
        return True

    def calculate(self, dataset) -> KPIResult:
        try:
            return self._calculate(dataset)
        except Exception as e:
            return self._build_low_confidence_result(str(e))

    def _calculate(self, dataset) -> KPIResult:
        stats = dataset.team_stats
        benchmarks = dataset.league_benchmarks
        recipe = dataset.recipe
        n_games = len(stats)

        indicators = []

        # --- 1. #shots open play vs sets ---
        # check the volume first 

        # --- 1. xGD Table vs Actual Table ---
        # shows the under performers and over performers
        # xGD vs actual GD ?
        # seperately xGF vs actual goals (finishing skills)
        # seperately xGA vs actual goals conceded (luck gk skills)
        # check the sustained divergance 10+ games (2-3 games is noise)

        # --- 2. rolling xGD for momentum ---
        # last 3-5 matches

        # --- 3. xG Per Shot ---    
        # check open play shots to see if they are shooting selectively

        # --- 4. xG from open play vs setpieces ---    
        # where does the threat come from

        # The four quadrants:
        # Top right — High xGF, Low xGA → Title contenders
        # Top left — Low xGF, Low xGA → Defensive, grind-out sides
        # Bottom right — High xGF, High xGA → Open, entertaining, volatile
        # Bottom left — Low xGF, High xGA → Relegation zone

        # xG breakdown
        # open play, set pieces, penalties, crosses
            #61 / “Corner” Shot direct from a corner kick
            #62 / “Free Kick” Shot is from a direct free kick
            #87 / “Open Play” Shot is not directly from a set-piece
            #88 / “Penalty” Shot is a penalty kick
            #65 / “Kick Off” Shot directly from kick off
        # inside box, outside box
        # left side right side middle
            # key pass id location(where did the pass originated)
            #location
            #body part (headers vs foot)
            
        
        
        # first half, second half 
        # winning vs loosing vs drawing
        # xG against top tier bottom tier
        # xG home vs away



        


        # --- 1. xG Table vs Actual Table ---
        ind = self._position_divergence(stats, benchmarks, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        # --- 2. Finishing Divergence ---
        ind = self._finishing_divergence(stats, n_games, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        # --- 3. xG Profile Quadrant ---
        ind = self._xg_profile_quadrant(stats, benchmarks, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        # --- 4. xG Source Breakdown ---
        ind = self._xg_source_breakdown(stats, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        # --- 5. xG Per Shot ---
        for ind in self._xg_per_shot(stats, benchmarks, recipe.confidence_score):
            indicators.append(ind)

        # --- 6. Opponent-Adjusted xGD ---
        ind = self._opponent_adjusted_xgd(stats, benchmarks, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        # --- 7. xG Under Pressure ---
        ind = self._xg_under_pressure(stats, recipe.confidence_score)
        if ind:
            indicators.append(ind)

        # --- Generate findings from combined indicators ---
        findings = self._generate_findings(indicators, recipe, n_games)

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
                'game_week': recipe.game_week,
                'blend_weights': {
                    'current': recipe.weight_current_season,
                    'prior': recipe.weight_prior_season,
                    'coach': recipe.weight_coach_history,
                }
            }
        )

    # ---------------------------------------------------------------------------
    # Indicator calculators
    # ---------------------------------------------------------------------------

    def _position_divergence(
        self, stats: pd.DataFrame, benchmarks: pd.DataFrame, confidence: float
    ) -> Indicator | None:
        """
        Compare actual league position to xG-implied league position.
        The gap reveals over/underperformance relative to underlying quality.

        TODO: implement once team_stats schema is defined.
        Requires: 'league_position', 'xgf_per90', 'xga_per90' columns.
        """
        # STUB — implement once data schema is confirmed
        # xgd_per90 = stats['xgf_per90'].mean() - stats['xga_per90'].mean()
        # actual_position = stats['league_position'].iloc[-1]
        # xg_position = self._estimate_xg_position(xgd_per90, benchmarks)
        # divergence = actual_position - xg_position
        return None

    def _finishing_divergence(
        self, stats: pd.DataFrame, n_games: int, confidence: float
    ) -> Indicator | None:
        """
        Compare actual goals to xGF to detect over/underperformance.
        Flags regression risk when overperformance is large.

        TODO: implement once team_stats schema is defined.
        Requires: 'goals_for', 'xgf' columns.
        """
        # STUB
        # goals = stats['goals_for'].sum()
        # xgf = stats['xgf'].sum()
        # diff = goals - xgf
        # interpretation = self._interpret_finishing(diff, n_games)
        return None

    def _xg_profile_quadrant(
        self, stats: pd.DataFrame, benchmarks: pd.DataFrame, confidence: float
    ) -> Indicator | None:
        """
        Position the team on the attack/defence xG quadrant.
        Quadrant: (xGF/90 vs league avg) x (xGA/90 vs league avg)

        TODO: implement once team_stats and league_benchmarks schema defined.
        """
        # STUB
        return None

    def _xg_source_breakdown(
        self, stats: pd.DataFrame, confidence: float
    ) -> Indicator | None:
        """
        Break down xGF by source: open play, set pieces, penalties.
        High set piece dependency (>40%) is flagged as tactical fragility.

        TODO: implement once team_stats schema is defined.
        Requires: 'xgf_open_play', 'xgf_set_piece', 'xgf_penalty' columns.
        """
        # STUB
        return None

    def _xg_per_shot(
        self, stats: pd.DataFrame, benchmarks: pd.DataFrame, confidence: float
    ) -> list[Indicator]:
        """
        Calculate xG per shot for attack and defence.
        Reveals shot selection quality independent of volume.

        TODO: implement once team_stats schema is defined.
        Requires: 'xgf', 'shots_for', 'xga', 'shots_against' columns.
        """
        # STUB
        return []

    def _opponent_adjusted_xgd(
        self, stats: pd.DataFrame, benchmarks: pd.DataFrame, confidence: float
    ) -> Indicator | None:
        """
        Adjust xGD for strength of schedule.
        A team with strong xGD against weak opponents is discounted.

        TODO: implement once opponent quality index is available in benchmarks.
        Requires: 'opponent_tier' column in stats.
        """
        # STUB
        return None

    def _xg_under_pressure(
        self, stats: pd.DataFrame, confidence: float
    ) -> Indicator | None:
        """
        Compare xGF/90 when winning vs drawing vs losing.
        Reveals system dependency on game state.

        TODO: implement once team_stats schema is defined.
        Requires: 'game_state' column in match-level stats.
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
    ) -> list[str]:
        """
        Generate natural language findings from calculated indicators.

        Findings lead with the insight. Indicators are the evidence.
        Each finding should be a complete, report-ready sentence.

        TODO: implement as indicators are built out.
        """
        findings = []

        # Sample size warning
        if not self._check_sample_size(n_games):
            findings.append(
                f"Early season — only {n_games} games available. "
                f"Indicators reflect blended prior and current season data. "
                f"Confidence will improve as the season progresses."
            )

        # Flag-driven findings
        if recipe.has_flag('new_coach'):
            findings.append(
                "New head coach in post — prior season tactical xG profile has "
                "limited predictive value. Monitor rolling xGD as the system embeds."
            )

        if recipe.has_flag('promoted'):
            findings.append(
                "Promoted club — prior season data adjusted for division-level "
                "quality difference. Current season sample prioritised."
            )

        # TODO: add indicator-driven findings as indicators are implemented
        # Example pattern:
        # pos_div = self._get_indicator(indicators, 'position_divergence')
        # if pos_div and pos_div.value > self.POSITION_DIVERGENCE_THRESHOLD:
        #     findings.append(
        #         f"Underlying performance ranks {abs(pos_div.value):.0f} places "
        #         f"above actual league position — positive regression likely."
        #     )

        return findings

    def _get_indicator(self, indicators: list[Indicator], id: str) -> Indicator | None:
        """Helper to retrieve an indicator by ID."""
        return next((i for i in indicators if i.id == id), None)

    def _interpret_finishing(self, diff: float, n_games: int) -> str:
        """Classify a finishing divergence value."""
        if diff > self.REGRESSION_RISK_THRESHOLD:
            return 'regression_risk'
        if diff > self.FINISHING_DIVERGENCE_THRESHOLD:
            return 'overperforming'
        if diff < -self.FINISHING_DIVERGENCE_THRESHOLD:
            return 'underperforming'
        return 'on_par'
