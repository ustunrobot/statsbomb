"""
Example usage of pressure intensity calculation.

Demonstrates how to use the pressure utility module to quantify
opponent pressure in event sequences.
"""

from pressure import calculate_sequence_pressure_intensity
from statsbomb_loader import load_match_events


def example_single_sequence():
    """Example 1: Analyze pressure in a single event sequence"""

    # Load match events
    match_file = 'path/to/match.json'
    events_df = load_match_events(match_file)

    # Convert to list of dicts
    events_list = events_df.to_dict('records')

    # Extract a sequence (e.g., first 20 events)
    sequence = events_list[:20]

    # Calculate pressure intensity
    pressure_metrics = calculate_sequence_pressure_intensity(
        sequence,
        opponent_team='Opponent Team Name',
        weighted=True  # Use event-type-specific weights
    )

    # Print results
    print(f"Sequence Pressure Analysis")
    print(f"─" * 50)
    print(f"Mean Pressure: {pressure_metrics['mean_pressure']:.3f} / 1.000")
    print(f"Max Pressure:  {pressure_metrics['max_pressure']:.3f}")
    print(f"Intensity:     {pressure_metrics['intensity_level']}")
    print(f"\nEvent Scores:")
    for i, score in enumerate(pressure_metrics['event_scores'][:10]):
        print(f"  Event {i+1}: {score:.3f}")

    print(f"\nDistribution:")
    for level, count in pressure_metrics['distribution'].items():
        print(f"  {level.capitalize()}: {count}")

    if pressure_metrics['pressure_peak']:
        peak = pressure_metrics['pressure_peak']
        print(f"\nPressure Peak:")
        print(f"  Event: {peak['event_type']}")
        print(f"  Player: {peak['player']}")
        print(f"  Score: {peak['pressure_score']:.3f}")
        print(f"  Intensity: {peak['intensity_level']}")


def example_possession_tracking():
    """Example 2: Analyze pressure across full possession sequences"""

    from statsbomb_loader import load_team_season
    from sequence_builder import build_sequences

    # Load team season
    team_events = load_team_season('Team Name', 'data')

    # Build sequences
    sequences = build_sequences(team_events, 'Team Name')

    # Analyze pressure in each sequence
    pressure_results = []

    for seq_idx, sequence in enumerate(sequences):
        seq_list = sequence.to_dict('records')

        pressure = calculate_sequence_pressure_intensity(
            seq_list,
            weighted=True
        )

        pressure_results.append({
            'sequence_id': seq_idx,
            'length': pressure['sequence_length'],
            'mean_pressure': pressure['mean_pressure'],
            'max_pressure': pressure['max_pressure'],
            'intensity': pressure['intensity_level'],
            'high_pressure_events': pressure['high_pressure_events'],
        })

    # Summary statistics
    mean_pressures = [p['mean_pressure'] for p in pressure_results]
    avg_pressure = sum(mean_pressures) / len(mean_pressures) if mean_pressures else 0

    print(f"\nSeason Possession Pressure Analysis")
    print(f"─" * 50)
    print(f"Total possessions: {len(pressure_results)}")
    print(f"Average pressure:  {avg_pressure:.3f}")
    print(f"\nTop 5 highest pressure possessions:")

    for i, p in enumerate(sorted(pressure_results, key=lambda x: x['mean_pressure'], reverse=True)[:5], 1):
        print(f"  {i}. Seq #{p['sequence_id']}: {p['mean_pressure']:.3f} ({p['intensity']})")


def example_windowed_analysis():
    """Example 3: Analyze pressure in time windows"""

    from statsbomb_loader import load_match_events

    # Load events
    match_file = 'path/to/match.json'
    events_df = load_match_events(match_file)
    events_list = events_df.to_dict('records')

    # Analyze by period
    periods = events_df['period'].unique()

    period_pressure = {}

    for period in periods:
        period_events = events_df[events_df['period'] == period].to_dict('records')

        pressure = calculate_sequence_pressure_intensity(
            period_events,
            weighted=True
        )

        period_pressure[f'Period {period}'] = {
            'mean': pressure['mean_pressure'],
            'max': pressure['max_pressure'],
            'intensity': pressure['intensity_level'],
            'events': len(period_events),
        }

    # Print summary
    print(f"\nPressure by Period")
    print(f"─" * 50)
    for period_name, metrics in period_pressure.items():
        print(f"{period_name}:")
        print(f"  Mean Pressure: {metrics['mean']:.3f}")
        print(f"  Intensity: {metrics['intensity']}")
        print(f"  Events: {metrics['events']}")


def example_team_comparison():
    """Example 4: Compare pressure exposure between teams"""

    from statsbomb_loader import load_match_events

    match_file = 'path/to/match.json'
    events_df = load_match_events(match_file)

    teams = events_df['team'].unique()

    comparison = {}

    for team in teams:
        team_events = events_df[events_df['team'] == team].to_dict('records')

        pressure = calculate_sequence_pressure_intensity(team_events)

        comparison[team] = {
            'mean_pressure': pressure['mean_pressure'],
            'max_pressure': pressure['max_pressure'],
            'high_pressure_events': pressure['high_pressure_events'],
            'intensity': pressure['intensity_level'],
            'actions': len(team_events),
        }

    # Print comparison
    print(f"\nTeam Pressure Comparison")
    print(f"─" * 70)
    print(f"{'Team':<25} {'Mean Pressure':<15} {'Intensity':<15} {'High Events':<15}")
    print(f"─" * 70)

    for team, metrics in comparison.items():
        print(f"{team:<25} {metrics['mean_pressure']:<15.3f} {metrics['intensity']:<15} {metrics['high_pressure_events']:<15}")


if __name__ == '__main__':
    print("=" * 70)
    print("PRESSURE INTENSITY CALCULATION EXAMPLES")
    print("=" * 70)

    print("\n1. Single Sequence Analysis")
    print("   (Uncomment to run)")
    # example_single_sequence()

    print("\n2. Possession Tracking")
    print("   (Uncomment to run)")
    # example_possession_tracking()

    print("\n3. Windowed Analysis")
    print("   (Uncomment to run)")
    # example_windowed_analysis()

    print("\n4. Team Comparison")
    print("   (Uncomment to run)")
    # example_team_comparison()

    print("\n" + "=" * 70)
    print("Usage:")
    print("  from utils.pressure import calculate_sequence_pressure_intensity")
    print("  ")
    print("  metrics = calculate_sequence_pressure_intensity(")
    print("      events_sequence=events_list,")
    print("      opponent_team='Team Name',")
    print("      weighted=True")
    print("  )")
    print("=" * 70)
