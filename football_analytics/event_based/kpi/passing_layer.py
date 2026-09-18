#!/usr/bin/env python3
"""Passing layer: Tracks player ball reception locations and median positions."""

import statistics
from typing import Dict, Any, List, Tuple
from ..metrics import Metric


class PlayerReceptionData:
    """Container for storing reception location data for a player."""

    def __init__(self):
        self.locations: List[Tuple[float, float]] = []  # List of (x, y) tuples
        self.name: str = ""
        self.jersey_number: int = 0

    def add_location(self, x: float, y: float) -> None:
        """Add a reception location."""
        self.locations.append((x, y))

    def get_median_position(self) -> Tuple[float, float]:
        """Calculate median x and y positions from all receptions."""
        if not self.locations:
            return 0.0, 0.0

        x_values = [loc[0] for loc in self.locations]
        y_values = [loc[1] for loc in self.locations]

        median_x = statistics.median(x_values) if x_values else 0.0
        median_y = statistics.median(y_values) if y_values else 0.0

        return median_x, median_y

    def get_reception_count(self) -> int:
        """Get total number of receptions."""
        return len(self.locations)


class PassingMatrix:
    """Container for tracking passes between player pairs."""

    def __init__(self):
        # Dictionary mapping (passer_id, receiver_id) -> pass_count
        self.passes: Dict[Tuple[int, int], int] = {}
        # Dictionary mapping player_id -> player_name (for reference)
        self.player_names: Dict[int, str] = {}

    def add_pass(self, passer_id: int, receiver_id: int, passer_name: str = "", receiver_name: str = "") -> None:
        """Record a pass from one player to another."""
        key = (passer_id, receiver_id)
        self.passes[key] = self.passes.get(key, 0) + 1

        # Store player names if provided
        if passer_name:
            self.player_names[passer_id] = passer_name
        if receiver_name:
            self.player_names[receiver_id] = receiver_name

    def get_matrix_dict(self) -> Dict:
        """Return passing matrix as a dictionary for export."""
        return {
            'passes': self.passes,
            'player_names': self.player_names
        }


class PassingField:
    """Container for player-based passing metrics."""

    def __init__(self):
        # Dictionary mapping player_id -> PlayerReceptionData
        self.players: Dict[int, PlayerReceptionData] = {}
        # Passing matrix for player-to-player passes
        self.passing_matrix: PassingMatrix = PassingMatrix()

    def add_player_reception(self, player_id: int, x: float, y: float) -> None:
        """Record a ball reception for a player."""
        if player_id not in self.players:
            self.players[player_id] = PlayerReceptionData()
        self.players[player_id].add_location(x, y)

    def get_all_player_metrics(self) -> Dict[str, Any]:
        """
        Get all player median positions as metrics.

        Returns a dictionary with keys like:
        - player_{player_id}_median_x
        - player_{player_id}_median_y
        - player_{player_id}_reception_count
        """
        metrics = {}

        for player_id, reception_data in self.players.items():
            median_x, median_y = reception_data.get_median_position()
            count = reception_data.get_reception_count()

            # Create metrics for median x position
            metric_x = Metric.default()
            metric_x.value = median_x
            metric_x.average = median_x
            metrics[f"player_{player_id}_median_x"] = metric_x

            # Create metrics for median y position
            metric_y = Metric.default()
            metric_y.value = median_y
            metric_y.average = median_y
            metrics[f"player_{player_id}_median_y"] = metric_y

            # Create metric for reception count
            metric_count = Metric.default()
            metric_count.value = float(count)
            metric_count.average = float(count)
            metrics[f"player_{player_id}_reception_count"] = metric_count

        return metrics


class PassingLayer:
    """Process player ball reception events and calculate median positions."""

    def __init__(self):
        self.layer_name = "passing"

    def initialize_team_aggregate(self, team_id: int, team_name: str) -> Dict:
        """Initialize aggregate structure for a team."""
        aggregate = {'team_name': team_name, 'matches': 0, 'players': {}}
        return aggregate

    def aggregate(self, team_aggregates: Dict, team_id: int, match_data: Dict) -> None:
        """
        Add a team's match passing data to the aggregate.

        Args:
            team_aggregates: Dictionary to accumulate stats
            team_id: Team ID
            match_data: Team data from single match (contains 'passing' key)
        """
        if team_id not in team_aggregates:
            team_aggregates[team_id] = self.initialize_team_aggregate(
                team_id, match_data.get('team_name', 'Unknown')
            )
            # Initialize passing matrix for the team aggregate
            team_aggregates[team_id]['passing_matrix'] = PassingMatrix()

        passing = match_data.get('passing')
        if not passing:
            return

        team_aggregates[team_id]['matches'] += 1

        # Aggregate player reception data across matches
        for player_id, reception_data in passing.players.items():
            if player_id not in team_aggregates[team_id]['players']:
                team_aggregates[team_id]['players'][player_id] = PlayerReceptionData()

            # Preserve player metadata (name and jersey number)
            if reception_data.name:
                team_aggregates[team_id]['players'][player_id].name = reception_data.name
            if reception_data.jersey_number:
                team_aggregates[team_id]['players'][player_id].jersey_number = reception_data.jersey_number

            # Add all locations from this match to the aggregated player data
            for x, y in reception_data.locations:
                team_aggregates[team_id]['players'][player_id].add_location(x, y)

        # Aggregate passing matrix data across matches
        if passing.passing_matrix:
            for (passer_id, receiver_id), pass_count in passing.passing_matrix.passes.items():
                key = (passer_id, receiver_id)
                team_aggregates[team_id]['passing_matrix'].passes[key] = \
                    team_aggregates[team_id]['passing_matrix'].passes.get(key, 0) + pass_count

            # Merge player names
            for player_id, player_name in passing.passing_matrix.player_names.items():
                if player_id not in team_aggregates[team_id]['passing_matrix'].player_names:
                    team_aggregates[team_id]['passing_matrix'].player_names[player_id] = player_name

    def finalize_team_aggregate(self, team_aggregate: Dict) -> None:
        """
        Finalize team aggregate by converting player data to metrics.

        Args:
            team_aggregate: Team aggregate dictionary to finalize
        """
        # Store player metadata separately for later use
        player_metadata = {}

        # Flatten all player metrics into the team_aggregate
        for player_id, reception_data in team_aggregate.get('players', {}).items():
            median_x, median_y = reception_data.get_median_position()
            count = reception_data.get_reception_count()

            team_aggregate[f"player_{player_id}_median_x"] = Metric.default()
            team_aggregate[f"player_{player_id}_median_x"].value = median_x
            team_aggregate[f"player_{player_id}_median_x"].average = median_x

            team_aggregate[f"player_{player_id}_median_y"] = Metric.default()
            team_aggregate[f"player_{player_id}_median_y"].value = median_y
            team_aggregate[f"player_{player_id}_median_y"].average = median_y

            team_aggregate[f"player_{player_id}_reception_count"] = Metric.default()
            team_aggregate[f"player_{player_id}_reception_count"].value = float(count)
            team_aggregate[f"player_{player_id}_reception_count"].average = float(count)

            # Store player metadata
            player_metadata[player_id] = {
                'name': reception_data.name,
                'jersey_number': reception_data.jersey_number
            }

        # Store metadata in team_aggregate for later retrieval
        team_aggregate['player_metadata'] = player_metadata

        # Store passing matrix data for later retrieval
        if 'passing_matrix' in team_aggregate:
            team_aggregate['passing_matrix_data'] = team_aggregate['passing_matrix'].get_matrix_dict()

    def process_event_row(self, event_row: Dict, accumulator, team_ids: Dict = None):
        """
        Process a single event for passing metrics.

        Args:
            event_row: Single event dictionary from StatsBomb data
            accumulator: KPIAccumulator instance to store results
            team_ids: Dictionary mapping team_id -> team_name (all teams in match)
        """
        # Extract player metadata from Starting XI events
        if self._is_starting_xi_event(event_row):
            self._extract_player_metadata(event_row, accumulator)
            return

        # Extract player metadata from Substitution events
        if self._is_substitution_event(event_row):
            self._extract_substitution_player_metadata(event_row, accumulator)
            return

        team_id = self._get_team_id(event_row)
        if not team_id:
            return

        # Get team data, initialize if needed
        team = accumulator.get_team(team_id)

        # Initialize passing section if not present
        if "passing" not in team:
            team["passing"] = PassingField()

        # Process Pass events for passing matrix
        if self._is_pass_event(event_row):
            self._process_pass_event(event_row, team["passing"])
            return

        # Check if this is a Ball Receipt event (type.id == 42)
        if not self._is_ball_receipt_event(event_row):
            return

        player_id = self._get_player_id(event_row)
        if not player_id:
            return

        location = self._get_location(event_row)
        if not location:
            return

        x, y = location

        # Record the reception location for this player
        team["passing"].add_player_reception(player_id, x, y)

    def _is_starting_xi_event(self, event_row: Dict) -> bool:
        """Check if event is a Starting XI event (type.id == 35)."""
        if "type" not in event_row:
            return False

        event_type = event_row["type"]
        if isinstance(event_type, dict):
            return event_type.get("id") == 35

        return event_type == 35

    def _is_substitution_event(self, event_row: Dict) -> bool:
        """Check if event is a Substitution event (type.id == 19)."""
        if "type" not in event_row:
            return False

        event_type = event_row["type"]
        if isinstance(event_type, dict):
            return event_type.get("id") == 19

        return event_type == 19

    def _extract_player_metadata(self, event_row: Dict, accumulator) -> None:
        """Extract player names and jersey numbers from Starting XI event."""
        team_id = self._get_team_id(event_row)
        if not team_id:
            return

        team = accumulator.get_team(team_id)

        # Initialize passing section if not present
        if "passing" not in team:
            team["passing"] = PassingField()

        # Extract player metadata from tactics.lineup
        tactics = event_row.get("tactics", {})
        lineup = tactics.get("lineup", [])

        for player_entry in lineup:
            player_info = player_entry.get("player", {})
            player_id = player_info.get("id")
            player_name = player_info.get("name", "")
            jersey_number = player_entry.get("jersey_number", 0)

            if player_id:
                if player_id not in team["passing"].players:
                    team["passing"].players[player_id] = PlayerReceptionData()

                team["passing"].players[player_id].name = player_name
                team["passing"].players[player_id].jersey_number = jersey_number

    def _extract_substitution_player_metadata(self, event_row: Dict, accumulator) -> None:
        """Extract player name from Substitution event (replacement player coming on)."""
        team_id = self._get_team_id(event_row)
        if not team_id:
            return

        team = accumulator.get_team(team_id)

        # Initialize passing section if not present
        if "passing" not in team:
            team["passing"] = PassingField()

        # Extract replacement player information
        substitution = event_row.get("substitution", {})
        replacement = substitution.get("replacement", {})
        player_id = replacement.get("id")
        player_name = replacement.get("name", "")

        if player_id and player_name:
            if player_id not in team["passing"].players:
                team["passing"].players[player_id] = PlayerReceptionData()

            team["passing"].players[player_id].name = player_name
            # Substitution events don't have jersey_number, so we'll keep it as 0 or skip if already set

    def _is_pass_event(self, event_row: Dict) -> bool:
        """Check if event is a Pass event (type.id == 30)."""
        if "type" not in event_row:
            return False

        event_type = event_row["type"]
        if isinstance(event_type, dict):
            return event_type.get("id") == 30

        return event_type == 30

    def _process_pass_event(self, event_row: Dict, passing_field: PassingField) -> None:
        """Extract and record a pass from one player to another."""
        # Get passer info
        passer_id = self._get_player_id(event_row)
        passer_name = event_row.get("player", {}).get("name", "") if isinstance(event_row.get("player"), dict) else ""

        # Get receiver info
        pass_data = event_row.get("pass", {})
        recipient = pass_data.get("recipient", {})
        receiver_id = recipient.get("id") if isinstance(recipient, dict) else None
        receiver_name = recipient.get("name", "") if isinstance(recipient, dict) else ""

        if passer_id and receiver_id:
            passing_field.passing_matrix.add_pass(passer_id, receiver_id, passer_name, receiver_name)

    def _is_ball_receipt_event(self, event_row: Dict) -> bool:
        """Check if event is a Ball Receipt event (type.id == 42)."""
        if "type" not in event_row:
            return False

        event_type = event_row["type"]
        if isinstance(event_type, dict):
            return event_type.get("id") == 42

        return event_type == 42

    def _get_team_id(self, event_row: Dict) -> int:
        """Extract team ID from event."""
        if "team" in event_row:
            team = event_row["team"]
            if isinstance(team, dict):
                return team.get("id")
            return team
        return None

    def _get_player_id(self, event_row: Dict) -> int:
        """Extract player ID from event."""
        if "player" in event_row:
            player = event_row["player"]
            if isinstance(player, dict):
                return player.get("id")
            return player
        return None

    def _get_location(self, event_row: Dict) -> Tuple[float, float]:
        """Extract x, y location from event."""
        if "location" not in event_row:
            return None

        location = event_row["location"]
        if isinstance(location, (list, tuple)) and len(location) >= 2:
            return (location[0], location[1])

        return None
