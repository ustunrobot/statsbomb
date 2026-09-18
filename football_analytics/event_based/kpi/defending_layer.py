#!/usr/bin/env python3
"""Defending layer: Tracks defensive actions and calculates defensive metrics."""

from typing import Dict, Any, List
from ..metrics import Metric


class DefensiveActionData:
    """Container for storing defensive action counts by type."""

    def __init__(self):
        self.pressure_count: int = 0
        self.interception_count: int = 0
        self.block_count: int = 0
        self.tackle_count: int = 0
        self.clearance_count: int = 0
        self.ball_recovery_count: int = 0
        self.fifty_fifty_count: int = 0
        self.yellow_card_count: int = 0
        self.red_card_count: int = 0

    def get_total_count(self) -> int:
        """Get total defensive actions."""
        return (
            self.pressure_count
            + self.interception_count
            + self.block_count
            + self.tackle_count
            + self.clearance_count
            + self.ball_recovery_count
            + self.fifty_fifty_count
        )

    def get_breakdown_dict(self) -> Dict[str, int]:
        """Return breakdown of defensive actions by type."""
        return {
            "pressure": self.pressure_count,
            "interception": self.interception_count,
            "block": self.block_count,
            "tackle": self.tackle_count,
            "clearance": self.clearance_count,
            "ball_recovery": self.ball_recovery_count,
            "fifty_fifty": self.fifty_fifty_count,
            "yellow_card": self.yellow_card_count,
            "red_card": self.red_card_count,
        }


class DefendingField:
    """Container for team-level defensive metrics."""

    def __init__(self):
        # Track total defensive actions
        self.total_defensive_actions = DefensiveActionData()
        # Heatmap for pressure locations: 20 rows x 30 columns (4m x 4m cells on 120x80 pitch)
        self.pressure_heatmap: List[List[int]] = [[0 for _ in range(30)] for _ in range(20)]

    def add_pressure(self, x: float = None, y: float = None) -> None:
        """Record a pressure action with optional location."""
        self.total_defensive_actions.pressure_count += 1
        if x is not None and y is not None:
            self._add_to_heatmap(x, y)

    def _add_to_heatmap(self, x: float, y: float) -> None:
        """Add a pressure event to the heatmap at (x, y) coordinates.

        Pitch dimensions: 120x80 (StatsBomb standard)
        Heatmap: 20 rows x 30 columns (4m x 4m cells)
        """
        # Map pitch coordinates (0-120, 0-80) to heatmap cells (0-29, 0-19)
        col = int((x / 120) * 30)
        row = int((y / 80) * 20)

        # Clamp to valid range
        col = max(0, min(29, col))
        row = max(0, min(19, row))

        # Increment heatmap cell
        self.pressure_heatmap[row][col] += 1

    def add_interception(self) -> None:
        """Record an interception action."""
        self.total_defensive_actions.interception_count += 1

    def add_block(self) -> None:
        """Record a block action."""
        self.total_defensive_actions.block_count += 1

    def add_tackle(self) -> None:
        """Record a tackle action."""
        self.total_defensive_actions.tackle_count += 1

    def add_clearance(self) -> None:
        """Record a clearance action."""
        self.total_defensive_actions.clearance_count += 1

    def add_ball_recovery(self) -> None:
        """Record a ball recovery action."""
        self.total_defensive_actions.ball_recovery_count += 1

    def add_fifty_fifty(self) -> None:
        """Record a 50/50 action."""
        self.total_defensive_actions.fifty_fifty_count += 1

    def add_yellow_card(self) -> None:
        """Record a yellow card."""
        self.total_defensive_actions.yellow_card_count += 1

    def add_red_card(self) -> None:
        """Record a red card."""
        self.total_defensive_actions.red_card_count += 1

    def add_second_yellow(self) -> None:
        """Record a second yellow card (equivalent to red card, reduces yellow count)."""
        self.total_defensive_actions.red_card_count += 1
        self.total_defensive_actions.yellow_card_count -= 1

    def get_total_actions(self) -> int:
        """Get total defensive actions count."""
        return self.total_defensive_actions.get_total_count()

    def get_breakdown(self) -> Dict[str, int]:
        """Get breakdown of defensive actions by type."""
        return self.total_defensive_actions.get_breakdown_dict()


class DefendingLayer:
    """Process defensive events and calculate defensive metrics."""

    def __init__(self):
        self.layer_name = "defending"

    def initialize_team_aggregate(self, team_id: int, team_name: str) -> Dict:
        """Initialize aggregate structure for a team."""
        aggregate = {
            "team_name": team_name,
            "matches": 0,
            "per_match_values": {}  # Store per-match metric values for trend tracking
        }
        return aggregate

    def aggregate(self, team_aggregates: Dict, team_id: int, match_data: Dict) -> None:
        """
        Add a team's match defending data to the aggregate.

        Args:
            team_aggregates: Dictionary to accumulate stats
            team_id: Team ID
            match_data: Team data from single match (contains 'defending' key)
        """
        if team_id not in team_aggregates:
            team_aggregates[team_id] = self.initialize_team_aggregate(
                team_id, match_data.get("team_name", "Unknown")
            )
            # Initialize defending field for the team aggregate
            team_aggregates[team_id]["defending"] = DefendingField()

        defending = match_data.get("defending")
        if not defending:
            return

        team_aggregates[team_id]["matches"] += 1

        # Store per-match values for trend tracking
        match_defending = defending.total_defensive_actions
        per_match = team_aggregates[team_id]["per_match_values"]

        # Initialize and store per-match values
        match_values = {
            "pressure_total": match_defending.pressure_count,
            "interception_total": match_defending.interception_count,
            "block_total": match_defending.block_count,
            "tackle_total": match_defending.tackle_count,
            "clearance_total": match_defending.clearance_count,
            "ball_recovery_total": match_defending.ball_recovery_count,
            "fifty_fifty_total": match_defending.fifty_fifty_count,
            "yellow_card_total": match_defending.yellow_card_count,
            "red_card_total": match_defending.red_card_count,
        }

        for metric_name, value in match_values.items():
            if metric_name not in per_match:
                per_match[metric_name] = []
            per_match[metric_name].append(float(value))

        # Aggregate defensive actions across matches
        team_agg_defending = team_aggregates[team_id]["defending"]

        team_agg_defending.total_defensive_actions.pressure_count += (
            match_defending.pressure_count
        )
        team_agg_defending.total_defensive_actions.interception_count += (
            match_defending.interception_count
        )
        team_agg_defending.total_defensive_actions.block_count += (
            match_defending.block_count
        )
        team_agg_defending.total_defensive_actions.tackle_count += (
            match_defending.tackle_count
        )
        team_agg_defending.total_defensive_actions.clearance_count += (
            match_defending.clearance_count
        )
        team_agg_defending.total_defensive_actions.ball_recovery_count += (
            match_defending.ball_recovery_count
        )
        team_agg_defending.total_defensive_actions.fifty_fifty_count += (
            match_defending.fifty_fifty_count
        )
        team_agg_defending.total_defensive_actions.yellow_card_count += (
            match_defending.yellow_card_count
        )
        team_agg_defending.total_defensive_actions.red_card_count += (
            match_defending.red_card_count
        )

        # Aggregate pressure heatmap across matches
        if hasattr(defending, 'pressure_heatmap'):
            for row_idx in range(20):
                for col_idx in range(30):
                    team_agg_defending.pressure_heatmap[row_idx][col_idx] += (
                        defending.pressure_heatmap[row_idx][col_idx]
                    )

    def finalize_team_aggregate(self, team_aggregate: Dict) -> None:
        """
        Finalize team aggregate by converting defensive data to metrics.

        Args:
            team_aggregate: Team aggregate dictionary to finalize
        """
        defending = team_aggregate.get("defending")
        if not defending:
            return

        matches = team_aggregate.get("matches", 1)
        if matches == 0:
            matches = 1

        # Get breakdown and totals
        breakdown = defending.get_breakdown()
        total_actions = defending.get_total_actions()

        # Create metric for total defensive actions
        total_metric = Metric.default()
        total_metric.value = float(total_actions)
        total_metric.average = float(total_actions / matches)
        team_aggregate["defensive_actions_total"] = total_metric

        # Create metrics for each defensive action type (total and per game)
        metric_keys = [
            ("pressure", "pressure_total"),
            ("interception", "interception_total"),
            ("block", "block_total"),
            ("tackle", "tackle_total"),
            ("clearance", "clearance_total"),
            ("ball_recovery", "ball_recovery_total"),
            ("fifty_fifty", "fifty_fifty_total"),
            ("yellow_card", "yellow_card_total"),
            ("red_card", "red_card_total"),
        ]

        for key, metric_name in metric_keys:
            count = breakdown.get(key, 0)

            # Store total count
            metric = Metric.default()
            metric.value = float(count)
            metric.average = float(count / matches)

            # Populate value_trend from per-match values
            per_match_values = team_aggregate.get("per_match_values", {})
            if metric_name in per_match_values:
                metric.value_trend = per_match_values[metric_name]

            team_aggregate[metric_name] = metric

        # Calculate discipline score: (4 * red_cards) + yellow_cards
        # Red cards are weighted 4x more since they result in ejection
        yellow_total = breakdown.get("yellow_card", 0)
        red_total = breakdown.get("red_card", 0)
        discipline_score = (4 * red_total) + yellow_total

        discipline_metric = Metric.default()
        discipline_metric.value = float(discipline_score)
        discipline_metric.average = float(discipline_score / matches)
        team_aggregate["discipline_score"] = discipline_metric

        # Store defending data for later retrieval
        team_aggregate["defending_data"] = {
            "total_actions": total_actions,
            "actions_per_match": total_actions / matches,
            "breakdown": breakdown,
        }

        # Store pressure heatmap as a Metric object
        pressure_heatmap_metric = Metric.default()
        pressure_heatmap_metric.heatmap = defending.pressure_heatmap
        team_aggregate["pressure_heatmap"] = pressure_heatmap_metric

    def process_event_row(self, event_row: Dict, accumulator, team_ids: Dict = None):
        """
        Process a single event for defensive metrics.

        Args:
            event_row: Single event dictionary from StatsBomb data
            accumulator: KPIAccumulator instance to store results
            team_ids: Dictionary mapping team_id -> team_name (all teams in match)
        """
        team_id = self._get_team_id(event_row)
        if not team_id:
            return

        # Get team data, initialize if needed
        team = accumulator.get_team(team_id)

        # Initialize defending section if not present
        if "defending" not in team:
            team["defending"] = DefendingField()

        # Process defensive events
        event_type_id = self._get_event_type_id(event_row)

        if event_type_id == 17:  # Pressure
            # Extract location if available
            location = self._get_location(event_row)
            if location:
                x, y = location
                team["defending"].add_pressure(x, y)
            else:
                team["defending"].add_pressure()
        elif event_type_id == 10:  # Interception
            team["defending"].add_interception()
        elif event_type_id == 6:  # Block
            team["defending"].add_block()
        elif event_type_id == 4:  # Duel
            # Check if it's a tackle duel
            duel = event_row.get("duel", {})
            if isinstance(duel, dict):
                duel_type = duel.get("type", {})
                if isinstance(duel_type, dict):
                    duel_type_id = duel_type.get("id")
                    if duel_type_id == 11:  # Tackle duel
                        team["defending"].add_tackle()
        elif event_type_id == 9:  # Clearance
            team["defending"].add_clearance()
        elif event_type_id == 2:  # Ball Recovery
            team["defending"].add_ball_recovery()
        elif event_type_id == 33:  # 50/50
            team["defending"].add_fifty_fifty()
        elif event_type_id == 24:  # Bad Behaviour
            # Check the bad behaviour card type
            bad_behaviour = event_row.get("bad_behaviour", {})
            if isinstance(bad_behaviour, dict):
                card = bad_behaviour.get("card", {})
                if isinstance(card, dict):
                    card_name = card.get("name", "")
                    if card_name == "Yellow Card":
                        team["defending"].add_yellow_card()
                    elif card_name == "Red Card":
                        team["defending"].add_red_card()
                    elif card_name == "Second Yellow":
                        team["defending"].add_second_yellow()

        # Handle under_pressure events: when ball-owner is under pressure, opposing team is pressing
        if self._is_under_pressure(event_row):
            # Get opposing team
            opposing_team_id = self._get_opposing_team_id(team_id, team_ids)
            if opposing_team_id:
                opposing_team = accumulator.get_team(opposing_team_id)
                if "defending" not in opposing_team:
                    opposing_team["defending"] = DefendingField()

                # Get event location and mirror it (flip x-coordinate)
                location = self._get_location(event_row)
                if location:
                    x, y = location
                    
                    mirrored_x = 120 - x     
                    mirrored_y = 80 - y               
                    opposing_team["defending"].add_pressure(mirrored_x, mirrored_y)
                else:
                    opposing_team["defending"].add_pressure()

    def _get_team_id(self, event_row: Dict) -> int:
        """Extract team ID from event."""
        if "team" in event_row:
            team = event_row["team"]
            if isinstance(team, dict):
                return team.get("id")
            return team
        return None

    def _get_event_type_id(self, event_row: Dict) -> int:
        """Extract event type ID from event."""
        if "type" not in event_row:
            return None

        event_type = event_row["type"]
        if isinstance(event_type, dict):
            return event_type.get("id")

        return event_type

    def _get_location(self, event_row: Dict):
        """Extract x, y location from event."""
        if "location" not in event_row:
            return None

        location = event_row["location"]
        if isinstance(location, (list, tuple)) and len(location) >= 2:
            return (location[0], location[1])

        return None

    def _is_under_pressure(self, event_row: Dict) -> bool:
        """Check if event has under_pressure field set to true."""
        return event_row.get("under_pressure", False) is True

    def _get_opposing_team_id(self, team_id: int, team_ids: Dict) -> int:
        """Get the opposing team ID from team_ids dictionary.

        Args:
            team_id: Current team ID
            team_ids: Dictionary mapping team_id -> team_name (all teams in match)

        Returns:
            Opposing team ID, or None if not found
        """
        if not team_ids:
            return None

        for other_team_id in team_ids.keys():
            if other_team_id != team_id:
                return other_team_id

        return None
