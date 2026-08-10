"""
Style of Play metrics — possession characteristics and playing patterns.

Measures how a team orchestrates possession: distribution across pitch zones,
passing characteristics, sequence depth, and tempo. High-level strategic indicators.
"""

import pandas as pd
import numpy as np
from typing import dict
from metrics.base import BaseMetric
from utils.pitch_zones import get_zone, is_progressive, PROGRESSIVE_PASS_THRESHOLD

# Metric thresholds
BUILDUP_X_THRESHOLD = 40.0
FINAL_THIRD_X = 80.0
SHORT_PASS_MAX = 25.0
LONG_PASS_MIN = 45.0
SEQ_THRESHOLDS = [5, 10, 15]
SET_PIECE_TECHNIQUES = ['Corner', 'Free Kick', 'Kick Off']


class StyleOfPlay(BaseMetric):
    """
    Analyze overall style and pattern of a team's possession play.

    Metrics computed:
    1. Possession Zone Distribution Index (PZDI)
    2. Pass Verticality & Length Index (PVLI)
    3. Sequence Depth Before Final Third (SDBF)
    4. Carry-to-Pass Progression Ratio (CPPR)
    5. Consecutive Pass Sequences (CSS)
    6. Ball Release Tempo (TEMPO)
    """

    def compute(self) -> dict:
        """
        Compute all style of play metrics.

        Returns:
            Flat dictionary with keys prefixed 'sop_' (style of play).
        """
        result = {}

        result.update(self._possession_zone_distribution())
        result.update(self._pass_verticality_length())
        result.update(self._sequence_depth_before_final_third())
        result.update(self._carry_to_pass_progression_ratio())
        result.update(self._consecutive_pass_sequences())
        result.update(self._ball_release_tempo())

        return result

    def _possession_zone_distribution(self) -> dict:
        """
        PZDI: Where on the pitch does the team spend possession time?

        Measures distribution of touches (pass starts, carries, ball receipts)
        across defensive, middle, and final thirds. High defensive % indicates
        patient, possession-dominant play. High final third % indicates
        aggressive, direct attacking approach.

        Returns:
            Dict with keys: sop_pzdi_def_pct, sop_pzdi_mid_pct, sop_pzdi_att_pct
        """
        team_events = self.filter_team_events()

        # Events representing possession touches
        touches = team_events[
            team_events['type_name'].isin(['Pass', 'Carry', 'Reception'])
        ].copy()

        if len(touches) == 0:
            return {
                'sop_pzdi_def_pct': 0.0,
                'sop_pzdi_mid_pct': 0.0,
                'sop_pzdi_att_pct': 0.0,
            }

        # Classify by zone
        zones = touches['x'].apply(lambda x: get_zone(x) if pd.notna(x) else None)

        def_pct = (zones == 'defensive').sum() / len(zones) * 100
        mid_pct = (zones == 'middle').sum() / len(zones) * 100
        att_pct = (zones == 'final').sum() / len(zones) * 100

        return {
            'sop_pzdi_def_pct': round(def_pct, 2),
            'sop_pzdi_mid_pct': round(mid_pct, 2),
            'sop_pzdi_att_pct': round(att_pct, 2),
        }

    def _pass_verticality_length(self) -> dict:
        """
        PVLI: How vertical (forward) vs lateral/backward are passes?

        Verticality = |end_x - start_x| / pass_length.
        High verticality (close to 1.0) = passes aimed directly forward.
        Low verticality = side-to-side, possession recycling.

        Mean pass length indicates directness: short = buildup-heavy,
        long = direct/long-ball approach.

        Returns:
            Dict with keys: sop_pvli_verticality, sop_pvli_mean_length
        """
        team_events = self.filter_team_events()
        passes = team_events[team_events['type_name'] == 'Pass'].copy()

        if len(passes) == 0:
            return {
                'sop_pvli_verticality': 0.0,
                'sop_pvli_mean_length': 0.0,
            }

        # Verticality: |dx| / length
        passes['dx'] = (passes['pass_end_x'] - passes['x']).abs()
        passes['verticality'] = passes['dx'] / (passes['pass_length'] + 0.1)  # Avoid div by zero
        passes['verticality'] = passes['verticality'].clip(0, 1)

        mean_vert = passes['verticality'].mean()
        mean_length = passes['pass_length'].mean()

        return {
            'sop_pvli_verticality': round(mean_vert, 3),
            'sop_pvli_mean_length': round(mean_length, 2),
        }

    def _sequence_depth_before_final_third(self) -> dict:
        """
        SDBF: How many passes/carries before entering final third?

        For sequences that reach final third (x > 80), count actions
        (passes + carries) before first event crosses 80.
        Indicates buildup patience: high depth = methodical, low = direct.

        Returns:
            Dict with keys: sop_sdbf_mean_depth, sop_sdbf_median_depth,
                           sop_sdbf_sequences_reaching_f3
        """
        from utils.sequence_builder import build_sequences

        sequences = build_sequences(self.events_df, self.team)

        depths = []
        sequences_f3 = 0

        for seq_df in sequences:
            if seq_df['reached_final_third'].iloc[0]:
                sequences_f3 += 1

                # Count actions before reaching final third
                actions_before_f3 = 0
                for _, event in seq_df.iterrows():
                    if pd.notna(event['x']) and event['x'] > FINAL_THIRD_X:
                        break
                    if event['type_name'] in ['Pass', 'Carry']:
                        actions_before_f3 += 1

                if actions_before_f3 > 0:
                    depths.append(actions_before_f3)

        mean_depth = np.mean(depths) if depths else 0.0
        median_depth = np.median(depths) if depths else 0.0

        return {
            'sop_sdbf_mean_depth': round(mean_depth, 2),
            'sop_sdbf_median_depth': round(median_depth, 2),
            'sop_sdbf_sequences_reaching_f3': int(sequences_f3),
        }

    def _carry_to_pass_progression_ratio(self) -> dict:
        """
        CPPR: Do progressive actions come from passes or carries?

        Ratio = carries / (carries + passes) for progressive actions.
        High ratio = dribble-heavy progression, low = pass-heavy progression.
        Also counts total progressive carries and passes.

        Returns:
            Dict with keys: sop_cppr_ratio, sop_cppr_prog_carries,
                           sop_cppr_prog_passes
        """
        team_events = self.filter_team_events()

        # Progressive passes
        passes = team_events[team_events['type_name'] == 'Pass'].copy()
        prog_passes = passes[
            (passes['pass_end_x'] - passes['x'] >= PROGRESSIVE_PASS_THRESHOLD)
        ]

        # Progressive carries
        carries = team_events[team_events['type_name'] == 'Carry'].copy()
        prog_carries = carries[
            (carries['carry_end_x'] - carries['x'] >= PROGRESSIVE_PASS_THRESHOLD)
        ]

        n_prog_passes = len(prog_passes)
        n_prog_carries = len(prog_carries)
        total = n_prog_passes + n_prog_carries

        ratio = (n_prog_carries / total * 100) if total > 0 else 0.0

        return {
            'sop_cppr_ratio': round(ratio, 2),
            'sop_cppr_prog_carries': int(n_prog_carries),
            'sop_cppr_prog_passes': int(n_prog_passes),
        }

    def _consecutive_pass_sequences(self) -> dict:
        """
        CSS: How many sequences of 5+, 10+, 15+ consecutive passes?

        Also measure forward distance covered in each threshold category.
        Indicates patient possession periods and buildup continuity.

        Returns:
            Dict with keys: sop_css_seq_{5,10,15}plus,
                           sop_css_prog_dist_{5,10,15}plus
        """
        team_events = self.filter_team_events()
        passes = team_events[team_events['type_name'] == 'Pass'].copy()

        if len(passes) == 0:
            return {
                'sop_css_seq_5plus': 0,
                'sop_css_seq_10plus': 0,
                'sop_css_seq_15plus': 0,
                'sop_css_prog_dist_5plus': 0.0,
                'sop_css_prog_dist_10plus': 0.0,
                'sop_css_prog_dist_15plus': 0.0,
            }

        # Mark successful passes
        passes['successful'] = passes['pass_type_name'].notna()

        result = {
            'sop_css_seq_5plus': 0,
            'sop_css_seq_10plus': 0,
            'sop_css_seq_15plus': 0,
            'sop_css_prog_dist_5plus': 0.0,
            'sop_css_prog_dist_10plus': 0.0,
            'sop_css_prog_dist_15plus': 0.0,
        }

        # Count consecutive sequences
        consecutive_count = 0
        sequence_distance = 0.0

        for _, pass_event in passes.iterrows():
            if pass_event['successful']:
                consecutive_count += 1
                sequence_distance += (pass_event['pass_end_x'] - pass_event['x']) if \
                    (pass_event['pass_end_x'] > pass_event['x']) else 0
            else:
                # Sequence ended
                if consecutive_count >= 5:
                    result['sop_css_seq_5plus'] += 1
                    result['sop_css_prog_dist_5plus'] += sequence_distance
                if consecutive_count >= 10:
                    result['sop_css_seq_10plus'] += 1
                    result['sop_css_prog_dist_10plus'] += sequence_distance
                if consecutive_count >= 15:
                    result['sop_css_seq_15plus'] += 1
                    result['sop_css_prog_dist_15plus'] += sequence_distance

                consecutive_count = 0
                sequence_distance = 0.0

        # Finalize distances
        result['sop_css_prog_dist_5plus'] = round(result['sop_css_prog_dist_5plus'], 2)
        result['sop_css_prog_dist_10plus'] = round(result['sop_css_prog_dist_10plus'], 2)
        result['sop_css_prog_dist_15plus'] = round(result['sop_css_prog_dist_15plus'], 2)

        return result

    def _ball_release_tempo(self) -> dict:
        """
        TEMPO: How quickly does the player with ball release it?

        Measured as time between receiving/starting carry and next pass.
        Excludes set pieces. High tempo = quick decision-making,
        low tempo = deliberate, controlled play.

        Returns:
            Dict with keys: sop_tempo_mean_release_sec,
                           sop_tempo_median_release_sec
        """
        team_events = self.filter_team_events().copy()

        # Convert timestamp to seconds for comparison
        def ts_to_seconds(ts):
            try:
                parts = ts.split(':')
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
            except:
                return 0.0

        team_events['ts_sec'] = team_events['timestamp'].apply(ts_to_seconds)

        release_times = []

        for idx in range(1, len(team_events)):
            curr = team_events.iloc[idx]
            prev = team_events.iloc[idx - 1]

            # If current is pass and previous was pass/carry by same player
            if curr['type_name'] == 'Pass' and prev['type_name'] in ['Pass', 'Carry'] and \
               curr['player'] == prev['player'] and \
               curr['pass_type_name'] not in SET_PIECE_TECHNIQUES:

                time_diff = curr['ts_sec'] - prev['ts_sec']
                if 0 < time_diff < 10:  # Reasonable bound
                    release_times.append(time_diff)

        mean_tempo = np.mean(release_times) if release_times else 0.0
        median_tempo = np.median(release_times) if release_times else 0.0

        return {
            'sop_tempo_mean_release_sec': round(mean_tempo, 2),
            'sop_tempo_median_release_sec': round(median_tempo, 2),
        }
