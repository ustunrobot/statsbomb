"""
Event Processor: Orchestrates event-by-event processing through KPI layers.

Responsibilities:
- Iterate through events in a match file
- Route each event to registered KPI layers
- Accumulate KPI results across teams
"""

from typing import Dict, Callable, List
from .kpi.xg_layer import XGLayer
from .kpi.xg_findings import XGFindingsLayer


class KPIAccumulator:
    """
    Holds accumulated KPI data for all teams in a match.

    Structure:
    {
        team_id: {
            'team_name': str,
            'xg': {...},
            'dribbling': {...},
            ...
        }
    }
    """

    def __init__(self):
        self.data: Dict = {}

    def initialize_team(self, team_id: int, team_name: str):
        """Initialize a team entry if not already present."""
        if team_id not in self.data:
            self.data[team_id] = {
                'team_id': team_id,
                'team_name': team_name,
            }

    def get_team(self, team_id: int) -> Dict:
        """Get or create team entry."""
        if team_id not in self.data:
            self.data[team_id] = {'team_id': team_id, 'team_name': 'Unknown'}
        return self.data[team_id]

    def get_all(self) -> Dict:
        """Return all accumulated KPI data."""
        return self.data


class EventProcessor:
    """
    Processes match events through registered KPI layers.

    Each KPI layer is responsible for one category of metrics
    (e.g., xG, dribbling, pressing, etc.) and processes every event.
    """

    def __init__(self):
        self.kpi_layers: List[Callable] = []
        self._register_default_layers()

    def _register_default_layers(self):
        """Register default KPI layers."""
        self.register_layer(XGLayer())

    def register_layer(self, layer):
        """
        Register a KPI layer.

        Layer must have a process_event_row(event_row, kpi_accumulator) method.
        """
        self.kpi_layers.append(layer)

    def process_event_file(
        self,
        events_dict: Dict,
        filename: str = "unknown",
    ) -> Dict:
        """
        Process all events in a match file through KPI layers.

        Args:
            events_dict: Dictionary of events (event_id -> event_data)
            filename: Name of the file (for logging)

        Returns:
            KPI accumulator with aggregated results for all teams.
        """
        accumulator = KPIAccumulator()

        # Pre-process: identify all teams in this match
        team_ids = self._extract_team_ids(events_dict)
        for team_id, team_name in team_ids.items():
            accumulator.initialize_team(team_id, team_name)

        # Process each event through all KPI layers
        event_count = 0
        for event_id, event_row in events_dict.items():
            # Skip non-dict events or malformed data
            if not isinstance(event_row, dict):
                continue

            event_count += 1

            # Route to each KPI layer
            for layer in self.kpi_layers:
                try:
                    layer.process_event_row(event_row, accumulator, team_ids)
                except Exception as e:
                    print(
                        f"Error in {layer.__class__.__name__} "
                        f"for event {event_id}: {e}"
                    )

        print(
            f"Processed {event_count} events, "
            f"{len(team_ids)} teams"
        )

        return accumulator.get_all()

    def _extract_team_ids(self, events_dict: Dict) -> Dict[int, str]:
        """
        Extract unique team IDs and names from events.

        Args:
            events_dict: Dictionary of events

        Returns:
            Dict mapping team_id -> team_name
        """
        teams = {}

        for event_row in events_dict.values():
            if not isinstance(event_row, dict):
                continue

            # Extract from possession_team field only
            if "possession_team" in event_row:
                team = event_row["possession_team"]
                if isinstance(team, dict):
                    team_id = team.get("id")
                    team_name = team.get("name", "Unknown")
                    if team_id and team_id not in teams:
                        teams[team_id] = team_name

            # Exit early once both teams found
            if len(teams) == 2:
                break

        return teams

    def aggregate_results(self, results_by_match: List[tuple]) -> Dict:
        """
        Aggregate match results across all KPI layers and teams.

        Args:
            results_by_match: List of (filename, match_results) tuples

        Returns:
            Dictionary with aggregated stats per team per layer:
            {
                'xg': {team_id: {stats}},
                'dribbling': {team_id: {stats}},
                ...
            }
        """
        aggregates_by_layer = {}

        for _, match_results in results_by_match:
            for team_id, team_data in match_results.items():
                for layer in self.kpi_layers:
                    layer_name = layer.layer_name
                    if layer_name not in aggregates_by_layer:
                        aggregates_by_layer[layer_name] = {}

                    layer.aggregate(
                        aggregates_by_layer[layer_name],
                        team_id,
                        team_data
                    )

        # Finalize aggregates by calculating derived fields
        self._finalize_aggregates(aggregates_by_layer)

        # Evaluate findings for each team
        findings_layer = XGFindingsLayer()
        aggregates_by_layer['xg_findings'] = self._evaluate_findings(findings_layer, aggregates_by_layer['xg'])

        return aggregates_by_layer

    def _finalize_aggregates(self, aggregates_by_layer: Dict) -> None:
        """
        Calculate derived Metric fields (value_pg, percentile, etc.) after aggregation.

        Args:
            aggregates_by_layer: Dictionary of aggregates to finalize in-place
        """
        from .metrics import Metric

        for layer_name, team_aggregates in aggregates_by_layer.items():
            # Get all metric field names (skip 'team_name' and 'matches')
            if not team_aggregates:
                continue

            sample_team = next(iter(team_aggregates.values()))
            metric_fields = [k for k in sample_team.keys()
                           if k not in ('team_name', 'matches') and isinstance(sample_team[k], Metric)]

            # For each metric field, calculate derived values and percentiles
            for field_name in metric_fields:
                self._calculate_metric_percentiles(team_aggregates, field_name)

    def _evaluate_findings(self, findings_layer: XGFindingsLayer, xg_aggregates: Dict) -> Dict:
        """
        Evaluate findings for all teams.

        Args:
            findings_layer: XGFindingsLayer instance
            xg_aggregates: Dictionary of teams with xG metrics

        Returns:
            Dictionary mapping team_id to list of findings
        """
        findings_by_team = {}
        for team_id, team_data in xg_aggregates.items():
            findings = findings_layer.evaluate_team(
                team_id,
                team_data.get('team_name', 'Unknown'),
                team_data
            )
            findings_by_team[team_id] = findings

        return findings_by_team

    def _calculate_metric_percentiles(self, team_aggregates: Dict, field_name: str) -> None:
        """
        Calculate value_pg, percentile, percentile_order, percentile_total, sample_size for a metric.

        Args:
            team_aggregates: Dictionary of teams with Metric objects
            field_name: Name of the metric field to process
        """
        # First pass: calculate value_pg and sample_size
        for team_id, team_data in team_aggregates.items():
            metric = team_data[field_name]
            matches = team_data['matches']
            metric.sample_size = matches
            if matches > 0:
                metric.value_pg = metric.value / matches

        # Second pass: rank teams by value_pg and calculate percentiles
        teams_by_value = sorted(
            team_aggregates.items(),
            key=lambda x: x[1][field_name].value_pg,
            reverse=True
        )

        total_teams = len(teams_by_value)

        for rank, (team_id, team_data) in enumerate(teams_by_value, 1):
            metric = team_data[field_name]
            metric.percentile_order = rank
            metric.percentile_total = total_teams
            # Percentile: (teams_behind / total_teams) * 100
            metric.percentile = ((total_teams - rank) / max(1, total_teams - 1)) * 100 if total_teams > 1 else 100.0
