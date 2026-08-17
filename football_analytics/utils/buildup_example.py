"""
Example usage of buildup_builder module.

Demonstrates how to extract and analyze buildup sequences.
"""

from statsbomb_loader import load_match_events
from sequence_builder import build_sequences
from buildup_builder import (
    extract_buildups_from_sequences,
    buildups_to_dataframe,
    summarize_buildups
)
import pandas as pd


def example_1_basic_extraction():
    """Example 1: Extract buildups from a match"""

    print("=" * 80)
    print("EXAMPLE 1: Basic Buildup Extraction")
    print("=" * 80)

    # Load match
    events_df = load_match_events('data/teams/Barnet/Week10_Barnet_vs_Accrington Stanley.json')

    # Build sequences
    sequences = build_sequences(events_df, team='Barnet')
    print(f"Found {len(sequences)} possession sequences")

    # Extract buildups
    buildups = extract_buildups_from_sequences(
        sequences=sequences,
        team='Barnet',
        opponent_team='Accrington Stanley'
    )
    print(f"Found {len(buildups)} buildup sequences")

    # Summary
    summary = summarize_buildups(buildups)
    print(f"\nSuccess rate: {summary['success_rate']}")
    print(f"Avg duration: {summary['avg_duration_sec']}s")
    print(f"Avg passes: {summary['avg_passes']}")


def example_2_detailed_analysis():
    """Example 2: Analyze buildup characteristics"""

    print("\n" + "=" * 80)
    print("EXAMPLE 2: Detailed Buildup Analysis")
    print("=" * 80)

    events_df = load_match_events('data/teams/Barnet/Week10_Barnet_vs_Accrington Stanley.json')
    sequences = build_sequences(events_df, team='Barnet')
    buildups = extract_buildups_from_sequences(
        sequences=sequences,
        team='Barnet',
        opponent_team='Accrington Stanley'
    )

    # Convert to DataFrame for analysis
    df = buildups_to_dataframe(buildups)

    print("\nBuildup Success Breakdown:")
    print(f"  Successful: {df['is_successful'].sum()} ({100*df['is_successful'].mean():.1f}%)")
    print(f"  Failed: {(~df['is_successful']).sum()} ({100*(~df['is_successful']).mean():.1f}%)")

    print("\nBuildup Duration:")
    print(f"  Min: {df['duration_sec'].min():.1f}s")
    print(f"  Max: {df['duration_sec'].max():.1f}s")
    print(f"  Avg: {df['duration_sec'].mean():.1f}s")

    print("\nBuildup Passes:")
    print(f"  Min: {df['n_passes'].min()}")
    print(f"  Max: {df['n_passes'].max()}")
    print(f"  Avg: {df['n_passes'].mean():.1f}")

    print("\nHow Buildups Ended:")
    print(df['end_reason'].value_counts())

    print("\nBuildup Distance Traveled:")
    print(f"  Min: {df['distance_traveled'].min():.1f}m")
    print(f"  Max: {df['distance_traveled'].max():.1f}m")
    print(f"  Avg: {df['distance_traveled'].mean():.1f}m")


def example_3_filter_buildups():
    """Example 3: Filter and analyze specific buildups"""

    print("\n" + "=" * 80)
    print("EXAMPLE 3: Filter Buildups by Criteria")
    print("=" * 80)

    events_df = load_match_events('data/teams/Barnet/Week10_Barnet_vs_Accrington Stanley.json')
    sequences = build_sequences(events_df, team='Barnet')
    buildups = extract_buildups_from_sequences(
        sequences=sequences,
        team='Barnet',
        opponent_team='Accrington Stanley'
    )

    df = buildups_to_dataframe(buildups)

    # Successful buildups only
    successful = df[df['is_successful']]
    print(f"\nSuccessful buildups: {len(successful)}")
    print(f"  Avg passes: {successful['n_passes'].mean():.1f}")
    print(f"  Avg duration: {successful['duration_sec'].mean():.1f}s")
    print(f"  Avg distance: {successful['distance_traveled'].mean():.1f}m")

    # Fast buildups (< 15 seconds)
    fast = df[df['duration_sec'] < 15]
    print(f"\nFast buildups (< 15s): {len(fast)}")
    print(f"  Success rate: {100*fast['is_successful'].mean():.1f}%")
    print(f"  Avg passes: {fast['n_passes'].mean():.1f}")

    # Long buildups (> 30 seconds)
    long = df[df['duration_sec'] > 30]
    print(f"\nLong buildups (> 30s): {len(long)}")
    print(f"  Success rate: {100*long['is_successful'].mean():.1f}%")
    print(f"  Avg passes: {long['n_passes'].mean():.1f}")

    # Lost possession during buildup
    lost = df[~df['is_successful'] & (df['end_reason'] == 'lost_possession')]
    print(f"\nBuildups ended in possession loss: {len(lost)}")
    if len(lost) > 0:
        print(f"  Avg distance before loss: {lost['distance_traveled'].mean():.1f}m")


def example_4_with_pressure():
    """Example 4: Analyze buildups with pressure metrics"""

    print("\n" + "=" * 80)
    print("EXAMPLE 4: Buildups with Pressure Analysis")
    print("=" * 80)

    events_df = load_match_events('data/teams/Barnet/Week10_Barnet_vs_Accrington Stanley.json')
    sequences = build_sequences(events_df, team='Barnet')

    # Extract with pressure metrics
    buildups = extract_buildups_from_sequences(
        sequences=sequences,
        team='Barnet',
        opponent_team='Accrington Stanley',
        include_pressure=True  # Enable pressure calculation
    )

    df = buildups_to_dataframe(buildups)

    print("\nBuildups with Pressure Metrics:")
    print(f"  Mean pressure across all buildups: {df['mean_pressure'].mean():.3f}")

    # High pressure buildups (mean_pressure > 0.5)
    high_pressure = df[df['mean_pressure'] > 0.5]
    print(f"\nHigh-pressure buildups (mean > 0.5): {len(high_pressure)}")
    if len(high_pressure) > 0:
        print(f"  Success rate under high pressure: {100*high_pressure['is_successful'].mean():.1f}%")
        print(f"  Avg pressure: {high_pressure['mean_pressure'].mean():.3f}")

    # Low pressure buildups (mean_pressure < 0.25)
    low_pressure = df[df['mean_pressure'] < 0.25]
    print(f"\nLow-pressure buildups (mean < 0.25): {len(low_pressure)}")
    if len(low_pressure) > 0:
        print(f"  Success rate in low pressure: {100*low_pressure['is_successful'].mean():.1f}%")
        print(f"  Avg pressure: {low_pressure['mean_pressure'].mean():.3f}")


def example_5_per_season_analysis():
    """Example 5: Analyze buildups across multiple matches (season)"""

    print("\n" + "=" * 80)
    print("EXAMPLE 5: Season-wide Buildup Analysis")
    print("=" * 80)

    from statsbomb_loader import load_team_season

    # Load team season
    team_events = load_team_season('Barnet', 'data')
    print(f"Loaded {len(team_events)} events from team season")

    # Get unique matches
    match_ids = team_events['match_id'].unique()
    print(f"Found {len(match_ids)} matches")

    # Analyze buildups across season
    all_buildups = []

    for match_id in match_ids:
        match_events = team_events[team_events['match_id'] == match_id]
        sequences = build_sequences(match_events, team='Barnet')

        buildups = extract_buildups_from_sequences(
            sequences=sequences,
            team='Barnet'
        )
        all_buildups.extend(buildups)

    print(f"\nTotal buildups in season: {len(all_buildups)}")

    summary = summarize_buildups(all_buildups)
    print(f"Success rate: {summary['success_rate']}")
    print(f"Avg duration: {summary['avg_duration_sec']}s")
    print(f"Avg passes: {summary['avg_passes']}")
    print(f"Avg distance: {summary['avg_distance_m']}m")


if __name__ == '__main__':
    # Run examples
    example_1_basic_extraction()
    example_2_detailed_analysis()
    example_3_filter_buildups()
    # example_4_with_pressure()  # Uncomment if pressure.py is working
    # example_5_per_season_analysis()  # Uncomment to analyze full season

    print("\n" + "=" * 80)
    print("Examples complete!")
    print("=" * 80)
