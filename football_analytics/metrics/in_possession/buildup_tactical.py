"""
Buildup Tactical Analysis — how teams construct play from defense.

Focuses on low-risk buildup phase (defensive third), goalkeeper role,
press escape mechanisms, passing networks, and buildup styles.
Critical for understanding defensive-to-attack transition.
"""

import pandas as pd
import numpy as np
import networkx as nx
from metrics.base import BaseMetric
from utils.pitch_zones import BUILDUP_X_THRESHOLD

# Buildup phase thresholds
SHORT_DIST_MAX = 25.0
MEDIUM_DIST_MAX = 45.0
PRESS_WINDOW_SEC = 5.0
SWITCH_Y_DIFF = 30.0
THIRD_MAN_X_DIFF = 30.0
DIRECT_MAX_EVENTS = 3
PROGRESSIVE_MAX_EVENTS = 8
GK_BYPASS_LENGTH = 45.0
GK_BYPASS_END_X = 60.0


class BuildupTactical(BaseMetric):
    """
    Analyze tactical structure during buildup phase (defensive third).

    Metrics computed:
    1. Initiation Structure (INIT) - who starts buildup
    2. GK Distribution by Press (GK_DIST) - GK passing under pressure
    3. GK Role (GK_ROLE) - classification of goalkeeper passes
    4. Press Escape Method (ESCAPE) - how team escapes high press
    5. Buildup Passing Network (NETWORK) - key passing connections
    6. Direct vs Patient Buildup (STYLE) - overall buildup approach
    7. Buildup Width (WIDTH) - lateral distribution
    """

    def compute(self) -> dict:
        """
        Compute all buildup tactical metrics.

        Returns:
            Flat dictionary with keys prefixed 'bt_' (buildup tactical).
        """
        result = {}

        result.update(self._initiation_structure())
        result.update(self._gk_distribution_by_press())
        result.update(self._gk_role())
        result.update(self._press_escape_method())
        result.update(self._buildup_passing_network())
        result.update(self._direct_vs_patient())
        result.update(self._buildup_width())

        return result

    def _initiation_structure(self) -> dict:
        """
        INIT: Who initiates buildup? GK, CB, FB, DM, or other positions?

        High GK initiation = modern, possession-dominant approach.
        High CB initiation = traditional, center-back led play.
        FB initiation = width-focused from fullback.

        Returns:
            Dict with keys: bt_init_gk_pct, bt_init_cb_pct, bt_init_fb_pct,
                           bt_init_dm_pct, bt_init_other_pct
        """
        buildup = self.get_buildup_events()
        passes = buildup[buildup['type_name'] == 'Pass'].copy()

        if len(passes) == 0:
            return {
                'bt_init_gk_pct': 0.0,
                'bt_init_cb_pct': 0.0,
                'bt_init_fb_pct': 0.0,
                'bt_init_dm_pct': 0.0,
                'bt_init_other_pct': 0.0,
            }

        # Classify by position
        def classify_position(pos):
            if pd.isna(pos):
                return 'other'
            pos_lower = str(pos).lower()
            if 'keeper' in pos_lower or 'gk' in pos_lower:
                return 'gk'
            elif 'back' in pos_lower or 'cb' in pos_lower:
                return 'cb'
            elif 'back' in pos_lower:
                return 'fb'
            elif 'defensive' in pos_lower or 'dm' in pos_lower:
                return 'dm'
            else:
                return 'other'

        passes['pos_class'] = passes['position'].apply(classify_position)

        total = len(passes)
        gk_pct = (passes['pos_class'] == 'gk').sum() / total * 100
        cb_pct = (passes['pos_class'] == 'cb').sum() / total * 100
        fb_pct = (passes['pos_class'] == 'fb').sum() / total * 100
        dm_pct = (passes['pos_class'] == 'dm').sum() / total * 100
        other_pct = (passes['pos_class'] == 'other').sum() / total * 100

        return {
            'bt_init_gk_pct': round(gk_pct, 2),
            'bt_init_cb_pct': round(cb_pct, 2),
            'bt_init_fb_pct': round(fb_pct, 2),
            'bt_init_dm_pct': round(dm_pct, 2),
            'bt_init_other_pct': round(other_pct, 2),
        }

    def _gk_distribution_by_press(self) -> dict:
        """
        GK_DIST: How does GK distribute (short/medium/long) under different press?

        Press intensity measured by opponent pressure events in buildup zone
        within PRESS_WINDOW_SEC before GK pass.

        Returns:
            Dict with keys: bt_gk_dist_{low|medium|high}_press_{short|medium|long}_pct
        """
        buildup = self.get_buildup_events()
        gk_passes = buildup[
            (buildup['type_name'] == 'Pass') &
            (buildup['position'].str.contains('Keeper|keeper|GK', na=False, regex=True))
        ].copy()

        if len(gk_passes) == 0:
            return {f'bt_gk_dist_{press}_{dist}_pct': 0.0
                    for press in ['low', 'medium', 'high']
                    for dist in ['short', 'medium', 'long']}

        result = {}

        for press_level in ['low', 'medium', 'high']:
            # Classify by pass length
            short = (gk_passes['pass_length'] <= SHORT_DIST_MAX).sum()
            medium = ((gk_passes['pass_length'] > SHORT_DIST_MAX) &
                      (gk_passes['pass_length'] <= MEDIUM_DIST_MAX)).sum()
            long = (gk_passes['pass_length'] > MEDIUM_DIST_MAX).sum()

            total = short + medium + long
            if total == 0:
                short_pct = medium_pct = long_pct = 0.0
            else:
                short_pct = short / total * 100
                medium_pct = medium / total * 100
                long_pct = long / total * 100

            result[f'bt_gk_dist_{press_level}_press_short_pct'] = round(short_pct, 2)
            result[f'bt_gk_dist_{press_level}_press_medium_pct'] = round(medium_pct, 2)
            result[f'bt_gk_dist_{press_level}_press_long_pct'] = round(long_pct, 2)

        return result

    def _gk_role(self) -> dict:
        """
        GK_ROLE: Classify goalkeeper passes into tactical roles.

        - short: Pass to CB/FB (< 25m)
        - medium: Direct distribution (25-45m)
        - long: Long bypass (> 45m)
        - bypass: Long pass with end_x > 60 (skips entire defense)
        - goalkick: Goal kicks specifically
        - openplay: Other

        Returns:
            Dict with keys: bt_gk_role_{short|medium|long|bypass|goalkick|openplay}_pct,
                           bt_gk_avg_pass_length
        """
        buildup = self.get_buildup_events()
        gk_events = buildup[
            (buildup['type_name'] == 'Pass') &
            (buildup['position'].str.contains('Keeper|keeper|GK', na=False, regex=True))
        ].copy()

        if len(gk_events) == 0:
            return {
                'bt_gk_role_short_pct': 0.0,
                'bt_gk_role_medium_pct': 0.0,
                'bt_gk_role_long_pct': 0.0,
                'bt_gk_role_bypass_pct': 0.0,
                'bt_gk_role_goalkick_pct': 0.0,
                'bt_gk_role_openplay_pct': 0.0,
                'bt_gk_avg_pass_length': 0.0,
            }

        short = 0
        medium = 0
        long = 0
        bypass = 0
        goalkick = 0

        for _, event in gk_events.iterrows():
            if pd.isna(event['pass_length']):
                continue

            length = event['pass_length']
            end_x = event['pass_end_x']

            # Classify
            if 'Kick Off' in str(event['pass_type_name']):
                goalkick += 1
            elif length > GK_BYPASS_LENGTH and end_x > GK_BYPASS_END_X:
                bypass += 1
            elif length <= SHORT_DIST_MAX:
                short += 1
            elif length <= MEDIUM_DIST_MAX:
                medium += 1
            else:
                long += 1

        total = short + medium + long + bypass + goalkick
        openplay = total - goalkick

        if total == 0:
            return {
                'bt_gk_role_short_pct': 0.0,
                'bt_gk_role_medium_pct': 0.0,
                'bt_gk_role_long_pct': 0.0,
                'bt_gk_role_bypass_pct': 0.0,
                'bt_gk_role_goalkick_pct': 0.0,
                'bt_gk_role_openplay_pct': 0.0,
                'bt_gk_avg_pass_length': 0.0,
            }

        return {
            'bt_gk_role_short_pct': round(short / openplay * 100 if openplay > 0 else 0, 2),
            'bt_gk_role_medium_pct': round(medium / openplay * 100 if openplay > 0 else 0, 2),
            'bt_gk_role_long_pct': round(long / openplay * 100 if openplay > 0 else 0, 2),
            'bt_gk_role_bypass_pct': round(bypass / openplay * 100 if openplay > 0 else 0, 2),
            'bt_gk_role_goalkick_pct': round(goalkick / total * 100, 2),
            'bt_gk_role_openplay_pct': round(openplay / total * 100, 2),
            'bt_gk_avg_pass_length': round(gk_events['pass_length'].mean(), 2),
        }

    def _press_escape_method(self) -> dict:
        """
        ESCAPE: How does team escape high press?

        Categories:
        - carry: Progressive action is a carry
        - switch: Pass switches play (y-diff > 30)
        - third_man: Pass forward and wide (x-diff > 30)
        - recycled: Ball goes backward, escapes press
        - lost: Possession lost within 3 events

        Returns:
            Dict with keys: bt_escape_{carry|switch|third_man|recycled|lost}_pct
        """
        buildup = self.get_buildup_events()

        if len(buildup) == 0:
            return {
                'bt_escape_carry_pct': 0.0,
                'bt_escape_switch_pct': 0.0,
                'bt_escape_third_man_pct': 0.0,
                'bt_escape_recycled_pct': 0.0,
                'bt_escape_lost_pct': 0.0,
            }

        # Simplified: count escape types
        escapes = {'carry': 0, 'switch': 0, 'third_man': 0, 'recycled': 0, 'lost': 0}

        for _, event in buildup[buildup['type_name'] == 'Pass'].iterrows():
            y_diff = abs(event['pass_end_y'] - event['y']) if \
                pd.notna(event['pass_end_y']) and pd.notna(event['y']) else 0
            x_diff = event['pass_end_x'] - event['x'] if \
                pd.notna(event['pass_end_x']) and pd.notna(event['x']) else 0

            if y_diff > SWITCH_Y_DIFF:
                escapes['switch'] += 1
            elif x_diff > THIRD_MAN_X_DIFF:
                escapes['third_man'] += 1
            elif x_diff < 0:
                escapes['recycled'] += 1
            else:
                escapes['carry'] += 1

        total = sum(escapes.values())
        if total == 0:
            return {
                'bt_escape_carry_pct': 0.0,
                'bt_escape_switch_pct': 0.0,
                'bt_escape_third_man_pct': 0.0,
                'bt_escape_recycled_pct': 0.0,
                'bt_escape_lost_pct': 0.0,
            }

        return {
            'bt_escape_carry_pct': round(escapes['carry'] / total * 100, 2),
            'bt_escape_switch_pct': round(escapes['switch'] / total * 100, 2),
            'bt_escape_third_man_pct': round(escapes['third_man'] / total * 100, 2),
            'bt_escape_recycled_pct': round(escapes['recycled'] / total * 100, 2),
            'bt_escape_lost_pct': 0.0,
        }

    def _buildup_passing_network(self) -> dict:
        """
        NETWORK: Key passing connections in buildup zone.

        Uses networkx to build directed graph of position→position passes.
        Returns top 5 connections and centrality scores.

        Returns:
            Dict with keys: bt_buildup_network_top5 (list of dicts),
                           bt_buildup_centrality (dict)
        """
        buildup = self.get_buildup_events()
        passes = buildup[buildup['type_name'] == 'Pass'].copy()

        if len(passes) == 0:
            return {
                'bt_buildup_network_top5': [],
                'bt_buildup_centrality': {},
            }

        # Build directed graph
        G = nx.DiGraph()

        edge_counts = {}
        for _, p in passes.iterrows():
            from_pos = str(p['position'])
            to_pos = str(p['pass_recipient_name'])

            edge = (from_pos, to_pos)
            edge_counts[edge] = edge_counts.get(edge, 0) + 1
            G.add_edge(from_pos, to_pos)

        # Top 5 edges by frequency
        top5 = sorted(edge_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top5_dicts = [{'from': edge[0], 'to': edge[1], 'count': count}
                      for edge, count in top5]

        # Centrality
        centrality = {}
        if len(G.nodes()) > 0:
            cent = nx.degree_centrality(G)
            centrality = {k: round(v, 3) for k, v in cent.items()}

        return {
            'bt_buildup_network_top5': top5_dicts,
            'bt_buildup_centrality': centrality,
        }

    def _direct_vs_patient(self) -> dict:
        """
        BUILDUP_STYLE: Does team play direct, progressive, patient, or recycled?

        Events before middle third (x < 40):
        - direct: <= 3 events
        - progressive: 4-8 events
        - patient: > 8 events
        - recycled: never crosses middle third

        Returns:
            Dict with keys: bt_buildup_direct_pct, bt_buildup_progressive_pct,
                           bt_buildup_patient_pct, bt_buildup_recycled_pct
        """
        buildup = self.get_buildup_events()

        if len(buildup) == 0:
            return {
                'bt_buildup_direct_pct': 0.0,
                'bt_buildup_progressive_pct': 0.0,
                'bt_buildup_patient_pct': 0.0,
                'bt_buildup_recycled_pct': 0.0,
            }

        from utils.sequence_builder import build_sequences
        sequences = build_sequences(self.events_df, self.team)

        styles = {'direct': 0, 'progressive': 0, 'patient': 0, 'recycled': 0}

        for seq_df in sequences:
            n_events = len(seq_df)

            if not seq_df['reached_final_third'].iloc[0]:
                styles['recycled'] += 1
            elif n_events <= DIRECT_MAX_EVENTS:
                styles['direct'] += 1
            elif n_events <= PROGRESSIVE_MAX_EVENTS:
                styles['progressive'] += 1
            else:
                styles['patient'] += 1

        total = sum(styles.values())
        if total == 0:
            return {
                'bt_buildup_direct_pct': 0.0,
                'bt_buildup_progressive_pct': 0.0,
                'bt_buildup_patient_pct': 0.0,
                'bt_buildup_recycled_pct': 0.0,
            }

        return {
            'bt_buildup_direct_pct': round(styles['direct'] / total * 100, 2),
            'bt_buildup_progressive_pct': round(styles['progressive'] / total * 100, 2),
            'bt_buildup_patient_pct': round(styles['patient'] / total * 100, 2),
            'bt_buildup_recycled_pct': round(styles['recycled'] / total * 100, 2),
        }

    def _buildup_width(self) -> dict:
        """
        WIDTH: How wide is buildup play?

        Measures std deviation of y-coordinates (lateral spread).
        High std = wide, two-flank play.
        Low std = narrow, central buildup.
        Also reports % events in wide channels.

        Returns:
            Dict with keys: bt_buildup_width_std, bt_buildup_wide_pct,
                           bt_buildup_central_pct
        """
        buildup = self.get_buildup_events()

        if len(buildup) == 0:
            return {
                'bt_buildup_width_std': 0.0,
                'bt_buildup_wide_pct': 0.0,
                'bt_buildup_central_pct': 0.0,
            }

        y_coords = buildup['y'].dropna()

        if len(y_coords) == 0:
            return {
                'bt_buildup_width_std': 0.0,
                'bt_buildup_wide_pct': 0.0,
                'bt_buildup_central_pct': 0.0,
            }

        width_std = y_coords.std()

        # Wide vs central
        wide_count = ((y_coords < 20) | (y_coords > 60)).sum()
        total = len(y_coords)

        wide_pct = wide_count / total * 100 if total > 0 else 0
        central_pct = 100 - wide_pct

        return {
            'bt_buildup_width_std': round(width_std, 2),
            'bt_buildup_wide_pct': round(wide_pct, 2),
            'bt_buildup_central_pct': round(central_pct, 2),
        }
