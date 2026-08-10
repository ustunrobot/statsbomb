"""
Tests for BuildupTactical metrics module.

Tests normal case, edge cases (no GK passes), and specific metric logic.
"""

import pytest
import pandas as pd
import numpy as np
from metrics.in_possession.buildup_tactical import BuildupTactical


@pytest.fixture
def synthetic_buildup_df():
    """Create synthetic buildup events with GK passes."""
    data = []

    # GK events in buildup zone (x < 40)
    for i in range(20):
        data.append({
            'id': f'event_{i}',
            'index': i,
            'timestamp': '00:45:00.000',
            'period': 1,
            'minute': 45,
            'second': 0,
            'type_name': 'Pass',
            'team': 'Arsenal',
            'player': 'Goalkeeper',
            'position': 'Goalkeeper',
            'under_pressure': None,
            'match_id': 123456,
            'source_file': 'test.json',
            'x': 10.0,
            'y': 40.0,
            'pass_length': 20.0 + (i % 30),
            'pass_angle': 0.5,
            'pass_end_x': 30.0 + (i % 40),
            'pass_end_y': 42.0,
            'pass_recipient_name': 'Defender',
            'pass_technique_name': None,
            'pass_height_name': 'Ground Pass',
            'pass_type_name': 'Long Ball' if i % 3 == 0 else 'Short Pass',
            'pass_success_probability': 0.85,
            'carry_end_x': np.nan,
            'carry_end_y': np.nan,
            'gk_end_x': np.nan,
            'gk_end_y': np.nan,
            'gk_type_name': None,
            'gk_position_name': None,
        })

    # CB events in buildup
    for i in range(20, 40):
        data.append({
            'id': f'event_{i}',
            'index': i,
            'timestamp': '00:45:00.000',
            'period': 1,
            'minute': 45,
            'second': 0,
            'type_name': 'Pass',
            'team': 'Arsenal',
            'player': 'Defender',
            'position': 'Center Back',
            'under_pressure': None,
            'match_id': 123456,
            'source_file': 'test.json',
            'x': 25.0,
            'y': 40.0,
            'pass_length': 10.0,
            'pass_angle': 0.5,
            'pass_end_x': 35.0,
            'pass_end_y': 42.0,
            'pass_recipient_name': 'Midfielder',
            'pass_technique_name': None,
            'pass_height_name': 'Ground Pass',
            'pass_type_name': 'Successful',
            'pass_success_probability': 0.9,
            'carry_end_x': np.nan,
            'carry_end_y': np.nan,
            'gk_end_x': np.nan,
            'gk_end_y': np.nan,
            'gk_type_name': None,
            'gk_position_name': None,
        })

    return pd.DataFrame(data)


class TestBuildupTacticalNormal:
    """Test normal case with buildup events."""

    def test_compute_returns_dict(self, synthetic_buildup_df):
        """Test that compute() returns a dictionary."""
        bt = BuildupTactical(synthetic_buildup_df, 'Arsenal')
        result = bt.compute()

        assert isinstance(result, dict)
        assert len(result) > 0

    def test_gk_role_classification(self, synthetic_buildup_df):
        """Test GK_ROLE metric with GK passes."""
        bt = BuildupTactical(synthetic_buildup_df, 'Arsenal')
        result = bt.compute()

        assert 'bt_gk_role_short_pct' in result
        assert 'bt_gk_role_medium_pct' in result
        assert 'bt_gk_role_long_pct' in result
        assert 'bt_gk_avg_pass_length' in result

        # GK avg pass length should be positive
        assert result['bt_gk_avg_pass_length'] > 0

    def test_initiation_structure(self, synthetic_buildup_df):
        """Test INIT metric (who initiates buildup)."""
        bt = BuildupTactical(synthetic_buildup_df, 'Arsenal')
        result = bt.compute()

        assert 'bt_init_gk_pct' in result
        assert 'bt_init_cb_pct' in result

        # Some initiations should be from GK or CB
        total = result['bt_init_gk_pct'] + result['bt_init_cb_pct'] + \
                result['bt_init_fb_pct'] + result['bt_init_dm_pct'] + \
                result['bt_init_other_pct']

        assert 95 <= total <= 105, f"Init percentages should sum to 100, got {total}"


class TestBuildupTacticalEdgeCases:
    """Test edge cases and error handling."""

    def test_no_gk_passes(self):
        """Test behavior when no GK passes exist."""
        data = []
        for i in range(20):
            data.append({
                'id': f'event_{i}',
                'index': i,
                'timestamp': '00:45:00.000',
                'period': 1,
                'minute': 45,
                'second': 0,
                'type_name': 'Pass',
                'team': 'Arsenal',
                'player': 'Defender',
                'position': 'Center Back',
                'under_pressure': None,
                'match_id': 123456,
                'source_file': 'test.json',
                'x': 30.0,
                'y': 40.0,
                'pass_length': 15.0,
                'pass_angle': 0.5,
                'pass_end_x': 40.0,
                'pass_end_y': 42.0,
                'pass_recipient_name': 'Midfielder',
                'pass_technique_name': None,
                'pass_height_name': 'Ground Pass',
                'pass_type_name': 'Successful',
                'pass_success_probability': 0.9,
                'carry_end_x': np.nan,
                'carry_end_y': np.nan,
                'gk_end_x': np.nan,
                'gk_end_y': np.nan,
                'gk_type_name': None,
                'gk_position_name': None,
            })

        df = pd.DataFrame(data)
        bt = BuildupTactical(df, 'Arsenal')
        result = bt.compute()

        # Should handle gracefully
        assert result['bt_gk_role_short_pct'] == 0.0
        assert result['bt_gk_avg_pass_length'] == 0.0

    def test_no_buildup_events(self):
        """Test when all events are outside buildup zone (x > 40)."""
        data = []
        for i in range(10):
            data.append({
                'id': f'event_{i}',
                'index': i,
                'timestamp': '00:45:00.000',
                'period': 1,
                'minute': 45,
                'second': 0,
                'type_name': 'Pass',
                'team': 'Arsenal',
                'player': f'Player {i}',
                'position': 'Forward',
                'under_pressure': None,
                'match_id': 123456,
                'source_file': 'test.json',
                'x': 90.0,  # All in final third
                'y': 40.0,
                'pass_length': 10.0,
                'pass_angle': 0.5,
                'pass_end_x': 95.0,
                'pass_end_y': 40.0,
                'pass_recipient_name': 'Striker',
                'pass_technique_name': None,
                'pass_height_name': 'Ground Pass',
                'pass_type_name': 'Successful',
                'pass_success_probability': 0.9,
                'carry_end_x': np.nan,
                'carry_end_y': np.nan,
                'gk_end_x': np.nan,
                'gk_end_y': np.nan,
                'gk_type_name': None,
                'gk_position_name': None,
            })

        df = pd.DataFrame(data)
        bt = BuildupTactical(df, 'Arsenal')
        result = bt.compute()

        # Buildup metrics should be zero/empty
        assert result['bt_init_gk_pct'] == 0.0


class TestBuildupTacticalLogic:
    """Test specific metric logic and calculations."""

    def test_press_escape_classification(self, synthetic_buildup_df):
        """Test ESCAPE metric classification."""
        bt = BuildupTactical(synthetic_buildup_df, 'Arsenal')
        result = bt.compute()

        assert 'bt_escape_carry_pct' in result
        assert 'bt_escape_switch_pct' in result
        assert 'bt_escape_recycled_pct' in result

        # Escape types should be percentages summing to ~100
        escape_total = result['bt_escape_carry_pct'] + result['bt_escape_switch_pct'] + \
                       result['bt_escape_third_man_pct'] + result['bt_escape_recycled_pct'] + \
                       result['bt_escape_lost_pct']

        assert 95 <= escape_total <= 105, f"Escape percentages should sum to 100, got {escape_total}"

    def test_buildup_width(self, synthetic_buildup_df):
        """Test WIDTH metric (lateral distribution)."""
        bt = BuildupTactical(synthetic_buildup_df, 'Arsenal')
        result = bt.compute()

        assert 'bt_buildup_width_std' in result
        assert 'bt_buildup_wide_pct' in result
        assert 'bt_buildup_central_pct' in result

        # Width percentages should sum to 100
        width_total = result['bt_buildup_wide_pct'] + result['bt_buildup_central_pct']
        assert 95 <= width_total <= 105, f"Width percentages should sum to 100, got {width_total}"
