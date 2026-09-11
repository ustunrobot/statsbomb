#!/usr/bin/env python3
"""Demo script for event processor."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.data_provider import DataProvider
from football_analytics.event_based.event_processor import EventProcessor
from football_analytics.event_based.metrics import Metric
from football_analytics.event_based.kpi.xg_findings import get_finding_evidence
from json import dumps
from dataclasses import asdict


def _serialize_aggregates(aggregates_by_layer):
    """Convert Metric objects to dictionaries for JSON serialization."""
    result = {}
    for layer_name, team_aggregates in aggregates_by_layer.items():
        if layer_name == 'xg_findings':
            # Special handling for findings
            result[layer_name] = {}
            for team_id, findings_list in team_aggregates.items():
                result[layer_name][team_id] = [
                    {
                        'team_name': f.team_name,
                        'category': f.category,
                        'finding_name': f.finding_name,
                    }
                    for f in findings_list
                ]
        else:
            result[layer_name] = {}
            for team_id, team_data in team_aggregates.items():
                result[layer_name][team_id] = {
                    'team_name': team_data['team_name'],
                    'matches': team_data['matches'],
                }
                for key, value in team_data.items():
                    if key not in ('team_name', 'matches'):
                        if isinstance(value, Metric):
                            result[layer_name][team_id][key] = asdict(value)
                        else:
                            result[layer_name][team_id][key] = value
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Analyze xG metrics and findings for a team')
    parser.add_argument('team', help='Team name to analyze')
    args = parser.parse_args()

    team_name = args.team

    provider = DataProvider()
    processor = EventProcessor()

    # Load and process matches
    matches = provider.get_matches()
    print(f"Processing {len(matches)} matches...")

    results_by_match = []
    for filename, events_dict in matches:        
        results = processor.process_event_file(events_dict, filename)
        results_by_match.append((filename, results))

    # Aggregate stats per team across all matches (delegated to KPI layers)
    aggregates_by_layer = processor.aggregate_results(results_by_match)


    
    sys.exit(1)


    # Find the team
    xg_agg = aggregates_by_layer['xg']
    findings_agg = aggregates_by_layer.get('xg_findings', {})

    selected_team_id = None
    selected_team_data = None
    for team_id, team_data in xg_agg.items():
        if team_data['team_name'].lower() == team_name.lower():
            selected_team_id = team_id
            selected_team_data = {team_id: team_data}
            break

    if not selected_team_data:
        print(f"\nTeam '{team_name}' not found.")
        print("\nAvailable teams:")
        for team_id, team_data in sorted(xg_agg.items(), key=lambda x: x[1]['team_name']):
            print(f"  - {team_data['team_name']}")
        sys.exit(1)

        # Display xG metrics
    print(f"\n\n{team_name} - Aggregate xG Metrics:")
    print("=" * 70)
    team_data = selected_team_data[selected_team_id]

    matches_count = team_data['matches']
    print(f"Matches Analyzed: {matches_count}\n")

    # Display all Metric fields for each metric in team data
    for field_name, field_value in sorted(team_data.items()):
        if field_name in ('team_id', 'team_name', 'matches'):
            continue

        if isinstance(field_value, Metric):
            print(f"{field_name.upper()}:")
            print(f"  Value: {field_value.value:.3f}")
            print(f"  Per Match: {field_value.value_pg:.3f}")
            print(f"  Percentile: {field_value.percentile:.1f}%")
            print(f"  Percentile Rank: {field_value.percentile_order}/{field_value.percentile_total}")
            print(f"  Sample Size: {field_value.sample_size}")
            print()

    # Export all xg metrics to Excel
    try:
        import pandas as pd
        from pathlib import Path

        xg_agg = aggregates_by_layer['xg']

        # Prepare flattened data for Excel
        rows = []
        for team_id, team_data in xg_agg.items():
            row = {
                'team_id': team_id,
                'team_name': team_data['team_name'],
                'matches': team_data['matches'],
            }

            # Flatten metric fields
            for field_name, field_value in sorted(team_data.items()):
                if field_name not in ('team_id', 'team_name', 'matches') and isinstance(field_value, Metric):
                    row[f'{field_name}_value'] = field_value.value
                    row[f'{field_name}_value_pg'] = field_value.value_pg
                    row[f'{field_name}_percentile'] = field_value.percentile
                    row[f'{field_name}_percentile_order'] = field_value.percentile_order
                    row[f'{field_name}_percentile_total'] = field_value.percentile_total
                    row[f'{field_name}_sample_size'] = field_value.sample_size

            rows.append(row)

        # Create DataFrame and export
        df = pd.DataFrame(rows)
        output_path = Path(__file__).parent.parent.parent / 'football_analytics' / 'data' / 'outputs' / 'xg_team_based.xlsx'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"Exported xg metrics to {output_path}")
    except ImportError:
        print("pandas or openpyxl not installed, skipping Excel export")

    # Display team findings
    print(f"\n\n{team_name} - Findings:")
    print("=" * 70)
    if selected_team_id in findings_agg:
        findings = findings_agg[selected_team_id]
        if findings:
            for finding in sorted(findings, key=lambda f: f.category):
                evidence = get_finding_evidence(finding.finding_name, selected_team_data[selected_team_id])
                if evidence:
                    print(f"  [{finding.category}] {finding.finding_name} ({evidence})")
                else:
                    print(f"  [{finding.category}] {finding.finding_name}")
        else:
            print("  No findings triggered")
    else:
        print("  No findings triggered")
