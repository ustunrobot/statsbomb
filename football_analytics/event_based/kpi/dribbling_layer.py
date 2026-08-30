"""
Dribbling Layer: Processes dribbling and ball-carrying metrics.

Metrics tracked per team:
- dribbles: Total dribble attempts
- dribbles_completed: Successful dribbles
- dribbles_success_rate: Percentage of successful dribbles
- progressive_carries: Ball carries moving toward opponent goal
"""

from typing import Dict, Optional


class DribblingLayer:
    """Process dribbling and ball-carrying events."""

    def __init__(self):
        self.layer_name = "dribbling"

    def _get_field_defaults(self) -> Dict:
        """Define dribbling fields with their default values (single match)."""
        return {
            "dribbles": 0,
            "dribbles_completed": 0,
            "dribbles_failed": 0,
            "dribbles_success_rate": 0.0,
        }

    def process_event_row(self, event_row: Dict, accumulator, team_ids: Dict = None):
        """
        Process a single event for dribbling metrics.

        Args:
            event_row: Single event dictionary from StatsBomb data
            accumulator: KPIAccumulator instance to store results
            team_ids: Dictionary mapping team_id -> team_name (all teams in match)
        """
        # TODO: Implement dribble event processing
        # Only process dribble events
        if not self._is_dribble_event(event_row):
            return

        team_id = self._get_team_id(event_row)
        if not team_id:
            return

        team = accumulator.get_team(team_id)

        # Initialize dribbling section if not present
        if "dribbling" not in team:
            team["dribbling"] = self._get_field_defaults().copy()

        # Extract dribble data
        is_successful = self._is_dribble_successful(event_row)

        team["dribbling"]["dribbles"] += 1
        if is_successful:
            team["dribbling"]["dribbles_completed"] += 1
        else:
            team["dribbling"]["dribbles_failed"] += 1

        # Update success rate
        total = team["dribbling"]["dribbles"]
        if total > 0:
            team["dribbling"]["dribbles_success_rate"] = (
                team["dribbling"]["dribbles_completed"] / total
            )

    def _is_dribble_event(self, event_row: Dict) -> bool:
        """Check if event is a dribble."""
        if "type" not in event_row:
            return False

        event_type = event_row["type"]
        if isinstance(event_type, dict):
            return event_type.get("name") == "Dribble"

        return event_type == "Dribble"

    def _get_team_id(self, event_row: Dict) -> Optional[int]:
        """Extract team ID from event."""
        if "team" in event_row and isinstance(event_row["team"], dict):
            return event_row["team"].get("id")
        return None

    def _is_dribble_successful(self, event_row: Dict) -> bool:
        """Check if dribble was successful."""
        if "dribble" not in event_row:
            return False

        dribble_data = event_row["dribble"]
        if not isinstance(dribble_data, dict):
            return False

        outcome = dribble_data.get("outcome")
        if isinstance(outcome, dict):
            return outcome.get("name") == "Complete"

        return outcome == "Complete"

    def initialize_team_aggregate(self, team_id: int, team_name: str) -> Dict:
        """Initialize aggregate structure for a team (dynamically from field defaults)."""
        aggregate = {'team_name': team_name, 'matches': 0}
        for field_name, default_value in self._get_field_defaults().items():
            aggregate[f'{field_name}'] = default_value
        return aggregate

    def aggregate(self, team_aggregates: Dict, team_id: int, match_data: Dict) -> None:
        """
        Add a team's match dribbling data to the aggregate.

        Args:
            team_aggregates: Dictionary to accumulate stats
            team_id: Team ID
            match_data: Team data from single match (contains 'dribbling' key)
        """
        if team_id not in team_aggregates:
            team_aggregates[team_id] = self.initialize_team_aggregate(
                team_id, match_data.get('team_name', 'Unknown')
            )

        dribbling = match_data.get('dribbling', {})
        team_aggregates[team_id]['matches'] += 1
        for field_name in self._get_field_defaults().keys():
            total_field = f'{field_name}'
            team_aggregates[team_id][total_field] += dribbling.get(field_name, 0)
