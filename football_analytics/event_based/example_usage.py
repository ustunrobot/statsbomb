"""
Example: Running the event-based analytics pipeline.

This demonstrates the full flow:
1. DataProvider collects match files
2. EventProcessor routes events through KPI layers
3. Results are accumulated and can be stored
"""

import json
from pathlib import Path
from .data_provider import DataProvider
from .event_processor import EventProcessor


def main():
    """Run a sample pipeline."""
    print("=" * 60)
    print("Event-Based Analytics Pipeline Example")
    print("=" * 60)

    # Step 1: Initialize data provider
    print("\n[1] Initializing DataProvider...")
    provider = DataProvider()

    # Step 2: Collect matches
    print("[2] Collecting matches...")
    matches = provider.get_matches(seasons=['25-26', '26-27'])
    print(f"    ✓ Loaded {len(matches)} matches")

    # Step 3: Initialize event processor
    print("\n[3] Initializing EventProcessor...")
    processor = EventProcessor()

    # Step 4: Process each match
    print("[4] Processing events...")
    all_results = {}

    for filename, events_dict in matches:
        print(f"\n    Processing: {filename}")
        print(f"      Events: {len(events_dict)}")

        # Process all events for this match through KPI layers
        kpi_results = processor.process_event_file(events_dict, filename)

        # Store results by filename
        all_results[filename] = kpi_results

        # Display summary for each team
        for team_id, team_data in kpi_results.items():
            team_name = team_data.get('team_name', 'Unknown')
            xg_data = team_data.get('xg', {})
            if xg_data:
                print(
                    f"      {team_name}: "
                    f"xGF={xg_data.get('xgf', 0):.2f}, "
                    f"goals={xg_data.get('goals', 0)}, "
                    f"shots={xg_data.get('shots', 0)}"
                )

    # Step 5: Display aggregated results
    print("\n[5] Summary Statistics")
    print("=" * 60)

    for filename, kpi_results in all_results.items():
        print(f"\n{filename}:")
        for team_id, team_data in kpi_results.items():
            print(f"  {team_data['team_name']}:")
            if "xg" in team_data:
                xg = team_data["xg"]
                print(f"    xGF: {xg.get('xgf', 0):.2f}")
                print(f"    xGA: {xg.get('xga', 0):.2f}")
                print(f"    Goals: {xg.get('goals', 0)}")
                print(f"    Shots: {xg.get('shots', 0)}")


if __name__ == "__main__":
    main()
