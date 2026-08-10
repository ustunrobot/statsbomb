"""
Tests for StyleOfPlay metrics module.

Tests normal case, edge cases (empty data), and specific metric logic.
"""

import pytest
import pandas as pd
import numpy as np
from metrics.in_possession.style_of_play import StyleOfPlay


@pytest.fixture
def synthetic_events_df():
    """Create synthetic match events for testing."""
    data = []

    # Create events with location and pass data
    for i in range(100):
        data.append({
            'id': f'event_{i}',
            'index': i,
            'timestamp': '00:45:00.000',
            'period': 1,
            'minute': 45,
            'second': 0,
            'type_name': 'Pass',
            'team': 'Arsenal',
            'player': f'Player {i % 11}',
            'position': 'Center Back' if i % 2 == 0 else 'Midfielder',
            'under_pressure': None,
            'match_id': 123456,
            'source_file': 'test.json',
            'x': 30.0 + (i % 80),  # Vary x from 30 to 110
            'y': 40.0,
            'pass_length': 15.0 + (i % 20),
            'pass_angle': 0.5,
            'pass_end_x': 40.0 + (i % 70),
            'pass_end_y': 42.0,
            'pass_recipient_name': f'Recipient {(i+1) % 11}',
            'pass_technique_name': None,
            'pass_height_name': 'Ground Pass',
            'pass_type_name': 'Successful' if i % 5 != 0 else 'Unsuccessful',
            'pass_success_probability': 0.85,
            'carry_end_x': np.nan,
            'carry_end_y': np.nan,
            'gk_end_x': np.nan,
            'gk_end_y': np.nan,
            'gk_type_name': None,
            'gk_position_name': None,
        })

    return pd.DataFrame(data)


class TestStyleOfPlayNormal:
    """Test normal case with realistic data."""

    def test_compute_returns_dict(self, synthetic_events_df):
        """Test that compute() returns a dictionary."""
        sop = StyleOfPlay(synthetic_events_df, 'Arsenal')
        result = sop.compute()

        assert isinstance(result, dict)
        assert len(result) > 0

    def test_possession_zone_distribution(self, synthetic_events_df):
        """Test PZDI metric calculation."""
        sop = StyleOfPlay(synthetic_events_df, 'Arsenal')
        result = sop.compute()

        assert 'sop_pzdi_def_pct' in result
        assert 'sop_pzdi_mid_pct' in result
        assert 'sop_pzdi_att_pct' in result

        # Percentages should sum to ~100
        total_pct = result['sop_pzdi_def_pct'] + result['sop_pzdi_mid_pct'] + result['sop_pzdi_att_pct']
        assert 95 <= total_pct <= 105, f"Zone percentages should sum to 100, got {total_pct}"

    def test_pass_verticality_length(self, synthetic_events_df):
        """Test PVLI metric calculation."""
        sop = StyleOfPlay(synthetic_events_df, 'Arsenal')
        result = sop.compute()

        assert 'sop_pvli_verticality' in result
        assert 'sop_pvli_mean_length' in result

        # Verticality should be between 0 and 1
        assert 0 <= result['sop_pvli_verticality'] <= 1
        assert result['sop_pvli_mean_length'] > 0


class TestStyleOfPlayEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_buildup_zone(self):
        """Test when no events in buildup zone."""
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
                'pass_recipient_name': 'Player',
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
        sop = StyleOfPlay(df, 'Arsenal')
        result = sop.compute()

        # Should handle gracefully
        assert result['sop_pzdi_def_pct'] == 0.0
        assert result['sop_pzdi_mid_pct'] == 0.0
        assert result['sop_pzdi_att_pct'] > 0

    def test_no_passes(self):
        """Test when team has no pass events."""
        data = []
        for i in range(10):
            data.append({
                'id': f'event_{i}',
                'index': i,
                'timestamp': '00:45:00.000',
                'period': 1,
                'minute': 45,
                'second': 0,
                'type_name': 'Carry',
                'team': 'Arsenal',
                'player': f'Player {i}',
                'position': 'Defender',
                'under_pressure': None,
                'match_id': 123456,
                'source_file': 'test.json',
                'x': 50.0,
                'y': 40.0,
                'pass_length': np.nan,
                'pass_angle': np.nan,
                'pass_end_x': np.nan,
                'pass_end_y': np.nan,
                'pass_recipient_name': None,
                'pass_technique_name': None,
                'pass_height_name': None,
                'pass_type_name': None,
                'pass_success_probability': np.nan,
                'carry_end_x': 55.0,
                'carry_end_y': 42.0,
                'gk_end_x': np.nan,
                'gk_end_y': np.nan,
                'gk_type_name': None,
                'gk_position_name': None,
            })

        df = pd.DataFrame(data)
        sop = StyleOfPlay(df, 'Arsenal')
        result = sop.compute()

        # Should handle gracefully with zeros
        assert result['sop_pvli_verticality'] == 0.0
        assert result['sop_pvli_mean_length'] == 0.0


class TestStyleOfPlaySequenceLogic:
    """Test specific metric logic."""

    def test_consecutive_pass_sequences_count(self, synthetic_events_df):
        """Test that CSS metric counts sequences correctly."""
        sop = StyleOfPlay(synthetic_events_df, 'Arsenal')
        result = sop.compute()

        assert 'sop_css_seq_5plus' in result
        assert 'sop_css_seq_10plus' in result
        assert 'sop_css_seq_15plus' in result

        # Should have counts (synthetic data has many passes)
        assert isinstance(result['sop_css_seq_5plus'], int)
