#!/usr/bin/env python3
"""Possession layer: Tracks carry and possession-related metrics."""

import math
from typing import Dict, Any
from ..metrics import Metric


class MetricsNode:
    """Nested metrics container supporting both dictionary and attribute access."""

    def __init__(self):
        self._data: Dict[str, Any] = {}

    def __getattr__(self, key: str) -> Any:
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        return self._data.get(key)

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith('_'):
            object.__setattr__(self, key, value)
        else:
            if '_data' not in self.__dict__:
                self.__dict__['_data'] = {}
            self._data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()


class PossessionField:
    """Container for possession-related metrics organized by direction."""

    def __init__(self):
        # Metric types to track
        self._metric_types = ['total']

        # Carry metrics: total carry distance and progressive carry distance (x-direction)
        self.carry_distance = MetricsNode()
        self.carry_x_distance = MetricsNode()

        # Final third passing metrics
        self.passes_in_final_third = MetricsNode()
        self.passes_successful_in_final_third = MetricsNode()

        # Pass ambition metrics (short/medium passes with tracked success probability)
        self.pass_ambition_count = MetricsNode()
        self.pass_ambition_success_probability = MetricsNode()

        # High pass metrics (overall)
        self.high_pass_count = MetricsNode()
        self.total_pass_count = MetricsNode()

        # High pass metrics by third
        self.high_pass_count_final_third = MetricsNode()
        self.total_pass_count_final_third = MetricsNode()

        self.high_pass_count_middle_third = MetricsNode()
        self.total_pass_count_middle_third = MetricsNode()

        self.high_pass_count_defensive_third = MetricsNode()
        self.total_pass_count_defensive_third = MetricsNode()

        # Throw-in metrics
        self.final_third_throw_in = MetricsNode()
        self.throw_in_landing_box = MetricsNode()

        # Corner metrics with location heatmaps
        self.left_corner = MetricsNode()
        self.right_corner = MetricsNode()

        # Aerial duel metrics by zone
        self.aerial_won = MetricsNode()
        self.aerial_won_final_third = MetricsNode()
        self.aerial_won_middle_third = MetricsNode()
        self.aerial_won_defensive_third = MetricsNode()

        self.aerial_lost = MetricsNode()
        self.aerial_lost_final_third = MetricsNode()
        self.aerial_lost_middle_third = MetricsNode()
        self.aerial_lost_defensive_third = MetricsNode()

        # Initialize all metric types for each metric
        for metric_type in self._metric_types:
            self.carry_distance[metric_type] = Metric.default()
            self.carry_x_distance[metric_type] = Metric.default()
            self.passes_in_final_third[metric_type] = Metric.default()
            self.passes_successful_in_final_third[metric_type] = Metric.default()
            self.pass_ambition_count[metric_type] = Metric.default()
            self.pass_ambition_success_probability[metric_type] = Metric.default()
            self.high_pass_count[metric_type] = Metric.default()
            self.total_pass_count[metric_type] = Metric.default()

            self.high_pass_count_final_third[metric_type] = Metric.default()
            self.total_pass_count_final_third[metric_type] = Metric.default()

            self.high_pass_count_middle_third[metric_type] = Metric.default()
            self.total_pass_count_middle_third[metric_type] = Metric.default()

            self.high_pass_count_defensive_third[metric_type] = Metric.default()
            self.total_pass_count_defensive_third[metric_type] = Metric.default()

            self.final_third_throw_in[metric_type] = Metric.default()
            throw_in_landing = Metric.default()
            throw_in_landing.heatmap = Metric.create_empty_heatmap()
            self.throw_in_landing_box[metric_type] = throw_in_landing

            # Corner metrics with heatmaps
            left_corner = Metric.default()
            left_corner.heatmap = Metric.create_empty_heatmap()
            self.left_corner[metric_type] = left_corner

            right_corner = Metric.default()
            right_corner.heatmap = Metric.create_empty_heatmap()
            self.right_corner[metric_type] = right_corner

            self.aerial_won[metric_type] = Metric.default()
            self.aerial_won_final_third[metric_type] = Metric.default()
            self.aerial_won_middle_third[metric_type] = Metric.default()
            self.aerial_won_defensive_third[metric_type] = Metric.default()

            self.aerial_lost[metric_type] = Metric.default()
            self.aerial_lost_final_third[metric_type] = Metric.default()
            self.aerial_lost_middle_third[metric_type] = Metric.default()
            self.aerial_lost_defensive_third[metric_type] = Metric.default()

    def __getattr__(self, key: str):
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        return object.__getattribute__(self, key)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as a flat dictionary with metric names."""
        metrics = {}
        # Include carry metrics
        for entity_name in ['carry_distance', 'carry_x_distance']:
            entity = getattr(self, entity_name)
            for metric_type in self._metric_types:
                if metric_type in entity._data:
                    key = f"{entity_name}_{metric_type}"
                    metrics[key] = entity[metric_type]

        # Include passing metrics
        for entity_name in ['passes_in_final_third', 'passes_successful_in_final_third',
                            'pass_ambition_count', 'pass_ambition_success_probability',
                            'high_pass_count', 'total_pass_count',
                            'high_pass_count_final_third', 'total_pass_count_final_third',
                            'high_pass_count_middle_third', 'total_pass_count_middle_third',
                            'high_pass_count_defensive_third', 'total_pass_count_defensive_third',
                            'final_third_throw_in', 'throw_in_landing_box',
                            'left_corner', 'right_corner']:
            entity = getattr(self, entity_name)
            for metric_type in self._metric_types:
                if metric_type in entity._data:
                    key = f"{entity_name}_{metric_type}"
                    metrics[key] = entity[metric_type]

        # Include aerial metrics
        for entity_name in ['aerial_won', 'aerial_won_final_third', 'aerial_won_middle_third', 'aerial_won_defensive_third',
                            'aerial_lost', 'aerial_lost_final_third', 'aerial_lost_middle_third', 'aerial_lost_defensive_third']:
            entity = getattr(self, entity_name, None)
            if entity is None:
                continue
            for metric_type in self._metric_types:
                if metric_type in entity._data:
                    key = f"{entity_name}_{metric_type}"
                    metrics[key] = entity[metric_type]

        return metrics


# Derived metrics definitions
# Type:
#   'ratio' - value is already normalized (use value directly for value_pg)
#   'total' - value is a total (divide by match count for value_pg)
DERIVED_METRICS = {
    'carry_efficiency': {
        'description': 'Efficiency of carries towards goal (carry_x_distance / carry_distance)',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('carry_x_distance_total', Metric.default()).value /
                               max(0.1, agg.get('carry_distance_total', Metric.default()).value))
    },
    'final_third_pass_success_ratio': {
        'description': 'Success rate of passes in final third (successful / total)',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('passes_successful_in_final_third_total', Metric.default()).value /
                               max(0.1, agg.get('passes_in_final_third_total', Metric.default()).value))
    },
    'aerial_total': {
        'description': 'Total aerial duels (won + lost)',
        'type': 'total',
        'formula': lambda agg: (agg.get('aerial_won_total', Metric.default()).value +
                               agg.get('aerial_lost_total', Metric.default()).value)
    },
    'aerial_won_ratio': {
        'description': 'Aerial duel win rate (won / total)',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('aerial_won_total', Metric.default()).value /
                               max(0.1, agg.get('aerial_won_total', Metric.default()).value +
                                   agg.get('aerial_lost_total', Metric.default()).value))
    },
    'aerial_won_final_third_ratio': {
        'description': 'Aerial win rate in final third',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('aerial_won_final_third_total', Metric.default()).value /
                               max(0.1, agg.get('aerial_won_final_third_total', Metric.default()).value +
                                   agg.get('aerial_lost_final_third_total', Metric.default()).value))
    },
    'aerial_won_middle_third_ratio': {
        'description': 'Aerial win rate in middle third',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('aerial_won_middle_third_total', Metric.default()).value /
                               max(0.1, agg.get('aerial_won_middle_third_total', Metric.default()).value +
                                   agg.get('aerial_lost_middle_third_total', Metric.default()).value))
    },
    'aerial_won_defensive_third_ratio': {
        'description': 'Aerial win rate in defensive third',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('aerial_won_defensive_third_total', Metric.default()).value /
                               max(0.1, agg.get('aerial_won_defensive_third_total', Metric.default()).value +
                                   agg.get('aerial_lost_defensive_third_total', Metric.default()).value))
    },
    'pass_ambition_score': {
        'description': 'Average expected success probability of short/medium passes with tracked success data',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('pass_ambition_success_probability_total', Metric.default()).value /
                               max(0.1, agg.get('pass_ambition_count_total', Metric.default()).value))
    },
    'high_pass_ratio': {
        'description': 'Ratio of high passes to total passes',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('high_pass_count_total', Metric.default()).value /
                               max(0.1, agg.get('total_pass_count_total', Metric.default()).value))
    },
    'high_pass_ratio_final_third': {
        'description': 'Ratio of high passes to total passes in final third',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('high_pass_count_final_third_total', Metric.default()).value /
                               max(0.1, agg.get('total_pass_count_final_third_total', Metric.default()).value))
    },
    'high_pass_ratio_middle_third': {
        'description': 'Ratio of high passes to total passes in middle third',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('high_pass_count_middle_third_total', Metric.default()).value /
                               max(0.1, agg.get('total_pass_count_middle_third_total', Metric.default()).value))
    },
    'high_pass_ratio_defensive_third': {
        'description': 'Ratio of high passes to total passes in defensive third',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('high_pass_count_defensive_third_total', Metric.default()).value /
                               max(0.1, agg.get('total_pass_count_defensive_third_total', Metric.default()).value))
    },
    'throw_in_landing_box_ratio': {
        'description': 'Ratio of throw-ins landing in penalty box to total final third throw-ins',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('throw_in_landing_box_total', Metric.default()).value /
                               max(0.1, agg.get('final_third_throw_in_total', Metric.default()).value))
    },
}


class PossessionLayer:
    """Process possession and carry events."""

    def __init__(self):
        self.layer_name = "possession"

    def initialize_team_aggregate(self, team_id: int, team_name: str) -> Dict:
        """Initialize aggregate structure for a team from PossessionField."""
        aggregate = {'team_name': team_name, 'matches': 0}
        # Initialize metrics using backward compatibility keys
        possession_field = PossessionField()
        all_metrics = possession_field.get_all_metrics()
        for key in all_metrics:
            metric = Metric.default()
            # Initialize heatmap for metrics that track spatial location
            if 'throw_in_landing_box' in key or 'left_corner' in key or 'right_corner' in key:
                metric.heatmap = Metric.create_empty_heatmap()
            aggregate[key] = metric
        return aggregate

    def aggregate(self, team_aggregates: Dict, team_id: int, match_data: Dict) -> None:
        """
        Add a team's match possession data to the aggregate.

        Args:
            team_aggregates: Dictionary to accumulate stats
            team_id: Team ID
            match_data: Team data from single match (contains 'possession' key)
        """
        if team_id not in team_aggregates:
            team_aggregates[team_id] = self.initialize_team_aggregate(
                team_id, match_data.get('team_name', 'Unknown')
            )

        possession = match_data.get('possession')
        if not possession:
            return

        team_aggregates[team_id]['matches'] += 1
        # Get flattened metrics from the multi-dimensional structure
        all_metrics = possession.get_all_metrics()
        for key, metric in all_metrics.items():
            if isinstance(metric, Metric) and key in team_aggregates[team_id]:
                agg_metric = team_aggregates[team_id][key]
                agg_metric.value += metric.value

                # Append metric value to trend history
                if agg_metric.value_trend is None:
                    agg_metric.value_trend = []
                agg_metric.value_trend.append(metric.value)

                # Aggregate heatmap data if present
                if metric.heatmap and agg_metric.heatmap:
                    for row_idx, row in enumerate(metric.heatmap):
                        for col_idx, cell_value in enumerate(row):
                            agg_metric.heatmap[row_idx][col_idx] += cell_value

    def process_event_row(self, event_row: Dict, accumulator, team_ids: Dict = None):
        """
        Process a single event for possession metrics.

        Args:
            event_row: Single event dictionary from StatsBomb data
            accumulator: KPIAccumulator instance to store results
            team_ids: Dictionary mapping team_id -> team_name (all teams in match)
        """
        # Extract key information
        team_id = self._get_team_id(event_row)
        if not team_id:
            return

        team = accumulator.get_team(team_id)

        # Initialize possession section if not present
        if "possession" not in team:
            team["possession"] = PossessionField()

        # Process carry events
        if self._is_carry_event(event_row):
            # Extract carry data
            carry_distance = self._get_carry_distance(event_row)
            carry_x_distance = self._get_carry_x_distance(event_row)

            if carry_distance is not None and carry_distance > 0:
                team["possession"].carry_distance.total.value += carry_distance

            if carry_x_distance is not None and carry_x_distance > 0:
                team["possession"].carry_x_distance.total.value += carry_x_distance

        # Process pass events
        if self._is_pass_event(event_row):
            # Count total passes
            team["possession"].total_pass_count.total.value += 1

            # Check if high pass
            is_high = self._is_high_pass(event_row)
            if is_high:
                team["possession"].high_pass_count.total.value += 1

            # Determine which third this pass is in
            pass_third = self._get_pitch_third(event_row)

            # Track passes by third
            if pass_third == 'final':
                team["possession"].total_pass_count_final_third.total.value += 1
                if is_high:
                    team["possession"].high_pass_count_final_third.total.value += 1
            elif pass_third == 'middle':
                team["possession"].total_pass_count_middle_third.total.value += 1
                if is_high:
                    team["possession"].high_pass_count_middle_third.total.value += 1
            elif pass_third == 'defensive':
                team["possession"].total_pass_count_defensive_third.total.value += 1
                if is_high:
                    team["possession"].high_pass_count_defensive_third.total.value += 1

            if self._is_in_final_third(event_row):
                team["possession"].passes_in_final_third.total.value += 1

                if self._is_pass_successful(event_row):
                    team["possession"].passes_successful_in_final_third.total.value += 1

            # Process pass ambition metrics
            success_prob = self._get_pass_ambition_success_probability(event_row)
            if success_prob is not None:
                team["possession"].pass_ambition_count.total.value += 1
                team["possession"].pass_ambition_success_probability.total.value += success_prob

        # Process throw-in events
        if self._is_throw_in(event_row):
            # Check if throw-in is in final third
            if self._is_in_final_third(event_row):
                team["possession"].final_third_throw_in.total.value += 1

            # Check if throw-in lands in penalty box
            is_in_box, end_location = self._is_throw_in_in_landing_box(event_row)
            if is_in_box and end_location:
                team["possession"].throw_in_landing_box.total.value += 1

                # Record location on heatmap (4m x 4m cells)
                x, y = end_location
                col = int(x / 4)
                row = int(y / 4)

                # Ensure indices are within bounds (0-29, 0-19)
                col = min(max(col, 0), 29)
                row = min(max(row, 0), 19)

                team["possession"].throw_in_landing_box.total.heatmap[row][col] += 1

        # Process corner events
        if self._is_left_corner(event_row):
            team["possession"].left_corner.total.value += 1

            # Record end_location (where corner is delivered to) on heatmap
            pass_data = event_row.get("pass")
            if pass_data and isinstance(pass_data, dict):
                end_location = pass_data.get("end_location")
                if end_location and len(end_location) >= 2:
                    x, y = end_location[0], end_location[1]
                    col = int(x / 4)
                    row = int(y / 4)

                    # Ensure indices are within bounds (0-29, 0-19)
                    col = min(max(col, 0), 29)
                    row = min(max(row, 0), 19)

                    team["possession"].left_corner.total.heatmap[row][col] += 1

        if self._is_right_corner(event_row):
            team["possession"].right_corner.total.value += 1

            # Record end_location (where corner is delivered to) on heatmap
            pass_data = event_row.get("pass")
            if pass_data and isinstance(pass_data, dict):
                end_location = pass_data.get("end_location")
                if end_location and len(end_location) >= 2:
                    x, y = end_location[0], end_location[1]
                    col = int(x / 4)
                    row = int(y / 4)

                    # Ensure indices are within bounds (0-29, 0-19)
                    col = min(max(col, 0), 29)
                    row = min(max(row, 0), 19)

                    team["possession"].right_corner.total.heatmap[row][col] += 1

        # Process aerial won events
        if self._is_aerial_won_event(event_row):
            team["possession"].aerial_won.total.value += 1
            third = self._get_pitch_third(event_row)
            if third == 'defensive':
                team["possession"].aerial_won_defensive_third.total.value += 1
            elif third == 'middle':
                team["possession"].aerial_won_middle_third.total.value += 1
            elif third == 'final':
                team["possession"].aerial_won_final_third.total.value += 1

        # Process aerial lost events
        if self._is_aerial_lost_event(event_row):
            team["possession"].aerial_lost.total.value += 1
            third = self._get_pitch_third(event_row)
            if third == 'defensive':
                team["possession"].aerial_lost_defensive_third.total.value += 1
            elif third == 'middle':
                team["possession"].aerial_lost_middle_third.total.value += 1
            elif third == 'final':
                team["possession"].aerial_lost_final_third.total.value += 1

    def _is_carry_event(self, event_row: Dict) -> bool:
        """Check if event is a carry."""
        if "type" not in event_row:
            return False

        event_type = event_row["type"]
        if isinstance(event_type, dict):
            return event_type.get("name") == "Carry"

        return event_type == "Carry"

    def _is_pass_event(self, event_row: Dict) -> bool:
        """Check if event is a pass."""
        if "type" not in event_row:
            return False

        event_type = event_row["type"]
        if isinstance(event_type, dict):
            return event_type.get("name") == "Pass"

        return event_type == "Pass"

    def _is_high_pass(self, event_row: Dict) -> bool:
        """Check if pass is a high pass (height.id == 3)."""
        try:
            if "pass" not in event_row:
                return False

            pass_data = event_row["pass"]
            if not isinstance(pass_data, dict):
                return False

            if "height" in pass_data:
                height = pass_data["height"]
                if isinstance(height, dict):
                    return height.get("id") == 3
            return False
        except (KeyError, TypeError):
            return False

    def _get_team_id(self, event_row: Dict) -> int:
        """Extract team ID from event."""
        if "team" in event_row:
            team = event_row["team"]
            if isinstance(team, dict):
                return team.get("id")
            return team
        return None

    def _get_carry_distance(self, event_row: Dict) -> float:
        """Calculate total carry distance (Euclidean distance from location to end location)."""
        try:
            if "location" not in event_row or "carry" not in event_row:
                return 0.0

            location = event_row["location"]
            carry = event_row["carry"]
            end_location = carry.get("end_location")

            if not end_location:
                return 0.0

            # Calculate Euclidean distance
            x_diff = end_location[0] - location[0]
            y_diff = end_location[1] - location[1]
            distance = math.sqrt(x_diff**2 + y_diff**2)
            return distance
        except (KeyError, TypeError, IndexError):
            return 0.0

    def _get_carry_x_distance(self, event_row: Dict) -> float:
        """Calculate progressive carry distance (x-direction only, towards goal)."""
        try:
            if "location" not in event_row or "carry" not in event_row:
                return 0.0

            location = event_row["location"]
            carry = event_row["carry"]
            end_location = carry.get("end_location")

            if not end_location:
                return 0.0

            # Calculate x-distance (progressive towards goal)
            # In StatsBomb, x increases towards goal (120m pitch)
            x_distance = end_location[0] - location[0]
            # Only count progressive carries (positive x movement towards goal)
            return max(0.0, x_distance)
        except (KeyError, TypeError, IndexError):
            return 0.0

    def _is_in_final_third(self, event_row: Dict) -> bool:
        """Check if pass is in final third (x >= 80 on 120m pitch)."""
        try:
            if "location" not in event_row:
                return False

            location = event_row["location"]
            x_location = location[0]
            # Final third is x >= 80 (last 40m of 120m pitch)
            return x_location >= 80.0
        except (KeyError, TypeError, IndexError):
            return False

    def _is_pass_successful(self, event_row: Dict) -> bool:
        """Check if pass was successful (has completion_target or no 'outcome' indicating failure)."""
        try:
            # Check for successful outcome
            if "outcome" in event_row:
                outcome = event_row["outcome"]
                if isinstance(outcome, dict):
                    outcome_name = outcome.get("name", "")
                    # Pass is unsuccessful if it's an incomplete pass
                    return outcome_name != "Incomplete"
                return outcome != "Incomplete"

            # If no outcome field, check for pass result
            if "pass" in event_row:
                pass_data = event_row["pass"]
                if isinstance(pass_data, dict):
                    # Completion target indicates successful pass
                    return "end_location" in pass_data or "recipient" in pass_data

            # Default to successful if no failure indicators
            return True
        except (KeyError, TypeError):
            return False

    def _is_aerial_won_event(self, event_row: Dict) -> bool:
        """
        Check if event is a won aerial duel.

        Types that can have aerial_won == TRUE:
        - Shot (type.id == 16)
        - Miscontrol (type.id == 38)
        - Clearance (type.id == 9)
        - Pass (type.id == 30)
        """
        try:
            if "type" not in event_row:
                return False

            event_type = event_row["type"]
            type_id = None

            if isinstance(event_type, dict):
                type_id = event_type.get("id")

            # Check if this event type can have aerial_won
            if type_id not in [16, 38, 9, 30]:
                return False

            # Check for aerial_won in the appropriate nested field
            aerial_won = False
            if type_id == 16 and "shot" in event_row:
                shot = event_row["shot"]
                if isinstance(shot, dict):
                    aerial_won = shot.get("aerial_won", False)
            elif type_id == 38 and "miscontrol" in event_row:
                miscontrol = event_row["miscontrol"]
                if isinstance(miscontrol, dict):
                    aerial_won = miscontrol.get("aerial_won", False)
            elif type_id == 9 and "clearance" in event_row:
                clearance = event_row["clearance"]
                if isinstance(clearance, dict):
                    aerial_won = clearance.get("aerial_won", False)
            elif type_id == 30 and "pass" in event_row:
                pass_data = event_row["pass"]
                if isinstance(pass_data, dict):
                    aerial_won = pass_data.get("aerial_won", False)            
            return aerial_won is True
        except (KeyError, TypeError, AttributeError):
            return False

    def _is_aerial_lost_event(self, event_row: Dict) -> bool:
        """
        Check if event is a lost aerial duel.

        Duel events (type.id == 4) with type.id == 10 (Aerial Lost)
        """
        try:
            if "type" not in event_row:
                return False

            event_type = event_row["type"]

            # Check if this is a Duel event (type.id == 4)
            type_id = None
            if isinstance(event_type, dict):
                type_id = event_type.get("id")

            if type_id != 4:
                return False

            # Check if duel type is Aerial Lost (duel.type.id == 10)
            if "duel" not in event_row:
                return False

            duel = event_row["duel"]
            if not isinstance(duel, dict) or "type" not in duel:
                return False

            duel_type = duel["type"]
            if isinstance(duel_type, dict):
                return duel_type.get("id") == 10
            return duel_type == 10
        except (KeyError, TypeError, AttributeError):
            return False

    def _get_pitch_third(self, event_row: Dict) -> str:
        """
        Determine which third of the pitch the event occurs in based on x-coordinate.

        Defensive third: x < 40
        Middle third: 40 <= x < 80
        Final third: x >= 80

        Returns: 'defensive', 'middle', 'final', or None if location not available
        """
        try:
            if "location" not in event_row:
                return None

            location = event_row["location"]
            x_location = location[0]

            if x_location < 40.0:
                return 'defensive'
            elif x_location < 80.0:
                return 'middle'
            else:
                return 'final'
        except (KeyError, TypeError, IndexError):
            return None

    def _is_throw_in(self, event_row: Dict) -> bool:
        """Check if event is a throw-in (Pass with type.id == 67)."""
        try:
            if "type" not in event_row or "pass" not in event_row:
                return False

            event_type = event_row["type"]
            type_id = event_type.get("id") if isinstance(event_type, dict) else None
            if type_id != 30:  # Pass event
                return False

            pass_data = event_row["pass"]
            if not isinstance(pass_data, dict) or "type" not in pass_data:
                return False

            pass_type = pass_data["type"]
            pass_type_id = pass_type.get("id") if isinstance(pass_type, dict) else None
            return pass_type_id == 67  # Throw-in
        except (KeyError, TypeError):
            return False

    def _is_throw_in_in_landing_box(self, event_row: Dict) -> tuple:
        """
        Check if throw-in lands in penalty box area.

        Returns: (is_in_box, end_location) tuple where:
        - is_in_box: True if throw-in lands in box (x >= 102, 18 <= y <= 62)
        - end_location: (x, y) tuple if found, else None
        """
        try:
            if not self._is_throw_in(event_row):
                return (False, None)

            pass_data = event_row["pass"]
            end_location = pass_data.get("end_location")
            if not end_location or len(end_location) < 2:
                return (False, None)

            x = end_location[0]
            y = end_location[1]

            # Check if in penalty box (x >= 102, 18 <= y <= 62)
            is_in_box = x >= 102 and 18 <= y <= 62
            return (is_in_box, (x, y))
        except (KeyError, TypeError):
            return (False, None)

    def _get_pass_ambition_success_probability(self, event_row: Dict) -> float:
        """
        Get success probability for pass ambition scoring.

        Conditions:
        - type.id == 30 (Pass)
        - pass.pass_success_probability IS NOT NULL
        - pass.height.id != 3 (not a high pass)
        - pass.length < 32 (less than 32 yards - short/medium pass)

        Returns: success_probability if conditions met, else None
        """
        try:
            if "type" not in event_row or "pass" not in event_row:
                return None

            # Check event type is Pass (30)
            event_type = event_row["type"]
            type_id = event_type.get("id") if isinstance(event_type, dict) else None
            if type_id != 30:
                return None

            pass_data = event_row["pass"]
            if not isinstance(pass_data, dict):
                return None

            # Check pass_success_probability exists and is not null
            success_prob = pass_data.get("pass_success_probability")
            if success_prob is None:
                return None

            # Check height is not 3 (High Pass)
            if "height" in pass_data:
                height = pass_data["height"]
                if isinstance(height, dict) and height.get("id") == 3:
                    return None

            # Check pass length < 32 yards
            pass_length = pass_data.get("length")
            if pass_length is not None and pass_length >= 32:
                return None

            return float(success_prob)
        except (KeyError, TypeError, ValueError):
            return None

    def _is_corner(self, event_row: Dict) -> bool:
        """Check if event is a corner kick (Pass with pass.type.id == 61)."""
        try:
            if "type" not in event_row or "pass" not in event_row:
                return False

            event_type = event_row["type"]
            type_id = event_type.get("id") if isinstance(event_type, dict) else None
            if type_id != 30:  # Pass event
                return False

            pass_data = event_row["pass"]
            if not isinstance(pass_data, dict) or "type" not in pass_data:
                return False

            pass_type = pass_data["type"]
            pass_type_id = pass_type.get("id") if isinstance(pass_type, dict) else None
            return pass_type_id == 61  # Corner
        except (KeyError, TypeError):
            return False

    def _is_left_corner(self, event_row: Dict) -> bool:
        """Check if corner is from left side (y < 40 on 80m pitch)."""
        try:
            if not self._is_corner(event_row):
                return False

            location = event_row.get("location")
            if not location or len(location) < 2:
                return False

            y = location[1]
            # Left side: y < 40 (first 40m of 80m pitch)
            return y < 40.0
        except (KeyError, TypeError, IndexError):
            return False

    def _is_right_corner(self, event_row: Dict) -> bool:
        """Check if corner is from right side (y >= 40 on 80m pitch)."""
        try:
            if not self._is_corner(event_row):
                return False

            location = event_row.get("location")
            if not location or len(location) < 2:
                return False

            y = location[1]
            # Right side: y >= 40 (last 40m of 80m pitch)
            return y >= 40.0
        except (KeyError, TypeError, IndexError):
            return False
