"""
XG Layer: Processes expected goals and shot-related metrics.

Metrics tracked per team:
- xGF: Expected goals for
- xGA: Expected goals against
- xGF_open_play: Expected goals from open play
- xGF_set_piece: Expected goals from set pieces
- xGF_free_kick: Expected goals from free kicks
- goals_for: Actual goals scored
- goals_against: Actual goals conceded
- shots: Total shot count
"""

from typing import Dict, Optional, Any
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


class XGField:
    """Multi-dimensional xG metrics structure.

    Dimensions:
    - Entity: xg, goal, shot, shot_target
    - Direction: for, against
    - Type: total, direct_corner, direct_free_kick, direct_kick_off, penalty,
             set_piece_corner, set_piece_throw_in, set_piece_free_kick,
             set_piece_total, open_play, header, inbox, outbox

    Access: xg_field.xg.for.open_play or xg_field["xg"]["for"]["open_play"]
    """

    def __init__(self):
        # Define metric types
        self._metric_types = [
            'total', 'direct_corner', 'direct_free_kick', 'direct_kick_off',
            'penalty', 'set_piece_corner', 'set_piece_throw_in', 'set_piece_free_kick',
            'set_piece_total', 'open_play', 'header', 'inbox', 'outbox', 'one_on_one'
        ]

        # Initialize multi-dimensional structure
        self.xg = self._init_entity()
        self.goal = self._init_entity()
        self.shot = self._init_entity()
        self.shot_target = self._init_entity()

    def _init_entity(self) -> MetricsNode:
        """Initialize an entity with for/against directions."""
        entity = MetricsNode()
        entity.for_dir = MetricsNode()
        entity.against = MetricsNode()

        # Initialize all metric types for each direction
        for metric_type in self._metric_types:
            entity.for_dir[metric_type] = Metric.default()
            entity.against[metric_type] = Metric.default()

        return entity

    def __getattr__(self, key: str):
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        return object.__getattribute__(self, key)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as a flat dictionary with coordinate-based keys (entity_direction_type)."""
        metrics = {}
        for entity_name in ['xg', 'goal', 'shot', 'shot_target']:
            entity = getattr(self, entity_name)
            for direction in ['for_dir', 'against']:
                dir_node = getattr(entity, direction)
                for metric_type in self._metric_types:
                    if metric_type in dir_node._data:
                        # Create coordinate-based key: entity_direction_type
                        key = f"{entity_name}_{direction.replace('_dir', '')}_{metric_type}"
                        metrics[key] = dir_node[metric_type]
        return metrics


# Derived metrics definitions using coordinate-based keys
# Keys format: entity_direction_type (e.g., xg_for_total, shot_for_open_play)
# Type:
#   'ratio' - value is already normalized (use value directly for value_pg)
#   'total' - value is a total (divide by match count for value_pg)
DERIVED_METRICS = {
    'xgf_direct_total': {
                'description': 'xGF total from direct shots',
                'type': 'total',
                'formula': lambda agg: (agg.get('xg_for_total', Metric.default()).value -
                                       agg.get('xg_for_set_piece_total', Metric.default()).value -
                                       agg.get('xg_for_open_play', Metric.default()).value)
            },
    'xgf_minus_goal': {
            'description': 'xGF minus Goals For',
            'type': 'total',
            'formula': lambda agg: (agg.get('xg_for_total', Metric.default()).value -
                                   agg.get('goal_for_total', Metric.default()).value)
        },
    'xga_minus_goal': {
                'description': 'xGA minus Goals Against',
                'type': 'total',
                'formula': lambda agg: (agg.get('xg_against_total', Metric.default()).value -
                                       agg.get('goal_against_total', Metric.default()).value)
            },
    'goal_per_xgf': {
            'description': 'Goals Per xGF',
            'type': 'ratio',
            'formula': lambda agg: (agg.get('goal_for_total', Metric.default()).value /
                                   max(1, agg.get('xg_for_total', Metric.default()).value))
        },
    'xgf_per_shot': {
        'description': 'Expected goals per shot',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('xg_for_total', Metric.default()).value /
                               max(1, agg.get('shot_for_total', Metric.default()).value))
    },
    'xgf_open_play_per_open_shots': {
        'description': 'Expected goals per open play shot',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('xg_for_open_play', Metric.default()).value /
                               max(1, agg.get('shot_for_open_play', Metric.default()).value))
    },
    'shots_outbox_per_shots': {
        'description': 'Outbox shot ratio in open play shots',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('shot_for_outbox', Metric.default()).value /
                               max(1, agg.get('shot_for_open_play', Metric.default()).value))
    },
    'xgf_outbox_per_xgf': {
        'description': 'Outbox xGF ratio in xGF',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('xg_for_outbox', Metric.default()).value /
                               max(1, agg.get('xg_for_total', Metric.default()).value))
    },
    'xgf_set_piece_ratio': {
        'description': 'Set piece xGF ratio in total xGF',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('xg_for_set_piece_total', Metric.default()).value /
                               max(1, agg.get('xg_for_total', Metric.default()).value))
    },
    'xgf_open_play_ratio': {
        'description': 'Open play xGF ratio in total xGF',
        'type': 'ratio',
        'formula': lambda agg: (agg.get('xg_for_open_play', Metric.default()).value /
                               max(1, agg.get('xg_for_total', Metric.default()).value))
    },
}


class XGLayer:
    """Process expected goals (xG) and shot events."""

    def __init__(self):
        self.layer_name = "xg"


    def process_event_row(self, event_row: Dict, accumulator, team_ids: Dict = None):
        """
        Process a single event for xG metrics.

        Args:
            event_row: Single event dictionary from StatsBomb data
            accumulator: KPIAccumulator instance to store results
            team_ids: Dictionary mapping team_id -> team_name (all teams in match)
        """
        # Only process shot events and own goals
        own_goal = False
        if not self._is_shot_event(event_row):
            if not self._is_own_goal_event(event_row):
                return
            else:
                own_goal = True

        # Extract key information
        team_id = self._get_team_id(event_row)
        if not team_id:
            return

        team = accumulator.get_team(team_id)

        # Find opposing team
        op_team_id = next((tid for tid in team_ids if tid != team_id), None) 
        op_team = accumulator.get_team(op_team_id) 

        # Initialize xg section if not present
        if "xg" not in team:
            team["xg"] = XGField()
        if op_team and "xg" not in op_team:
            op_team["xg"] = XGField()

        if own_goal:
            # For own goals, increment opponent's and teams' goals only
            team["xg"].goal.for_dir.total.value += 1
            op_team["xg"].goal.against.total.value += 1
            return
        
        # Extract shot data
        xg_value = self._get_xg_value(event_row)
        if xg_value is None:
            xg_value = 0.0

        xg_shot_uplift_value = self._get_xg_shot_uplift_value(event_row)

        is_goal = self._is_goal(event_row)
        shot_type = self._get_shot_type(event_row)
        body_part = self._get_body_part(event_row)
        is_header = body_part.lower() == "head"
        is_one_on_one = self._is_one_on_one(event_row)        
        shot_location = self._get_shot_location(event_row)        
        is_on_target = self._is_on_target(event_row)

        xg = team["xg"]
        op_xg = op_team["xg"]

        # Update totals
        xg.xg.for_dir.total.value += xg_value
        xg.shot.for_dir.total.value += 1
        op_xg.xg.against.total.value += xg_value
        op_xg.shot.against.total.value += 1
        if shot_location == "inbox":
            xg.xg.for_dir.inbox.value += xg_value
            xg.shot.for_dir.inbox.value += 1
            op_xg.xg.against.inbox.value += xg_value
            op_xg.shot.against.inbox.value += 1
        else:
            xg.xg.for_dir.outbox.value += xg_value
            xg.shot.for_dir.outbox.value += 1
            op_xg.xg.against.outbox.value += xg_value
            op_xg.shot.against.outbox.value += 1

        if is_on_target:
            xg.shot_target.for_dir.total.value += 1
            op_xg.shot_target.against.total.value += 1

        if is_goal:
            xg.goal.for_dir.total.value += 1
            op_xg.goal.against.total.value += 1
            if shot_location == "inbox":
                xg.goal.for_dir.inbox.value += 1
                op_xg.goal.against.inbox.value += 1
            else:
                xg.goal.for_dir.outbox.value += 1
                op_xg.goal.against.outbox.value += 1
        
        # Update body part
        if is_header:
            xg.xg.for_dir.header.value += xg_value
            op_xg.xg.against.header.value += xg_value
            xg.shot.for_dir.header.value += 1
            op_xg.shot.against.header.value += 1    
            if is_on_target:
                xg.shot_target.for_dir.header.value += 1
                op_xg.shot_target.against.header.value += 1
            if is_goal:
                xg.goal.for_dir.header.value += 1
                op_xg.goal.against.header.value += 1

        # Update one on one
        if is_one_on_one:
            xg.xg.for_dir.one_on_one.value += xg_value
            op_xg.xg.against.one_on_one.value += xg_value
            xg.shot.for_dir.one_on_one.value += 1
            op_xg.shot.against.one_on_one.value += 1
            if is_on_target:
                xg.shot_target.for_dir.one_on_one.value += 1
                op_xg.shot_target.against.one_on_one.value += 1
            if is_goal:
                xg.goal.for_dir.one_on_one.value += 1
                op_xg.goal.against.one_on_one.value += 1

        # Update direct corner
        if shot_type == "direct_corner":
            xg.xg.for_dir.direct_corner.value += xg_value
            op_xg.xg.against.direct_corner.value += xg_value
            xg.shot.for_dir.direct_corner.value += 1
            op_xg.shot.against.direct_corner.value += 1
            if is_on_target:
                xg.shot_target.for_dir.direct_corner.value += 1
                op_xg.shot_target.against.direct_corner.value += 1
            if is_goal:
                xg.goal.for_dir.direct_corner.value += 1
                op_xg.goal.against.direct_corner.value += 1

        # Update direct free kick
        elif shot_type == "direct_free_kick":
            xg.xg.for_dir.direct_free_kick.value += xg_value
            op_xg.xg.against.direct_free_kick.value += xg_value
            xg.shot.for_dir.direct_free_kick.value += 1
            op_xg.shot.against.direct_free_kick.value += 1
            if is_on_target:
                xg.shot_target.for_dir.direct_free_kick.value += 1
                op_xg.shot_target.against.direct_free_kick.value += 1
            if is_goal:
                xg.goal.for_dir.direct_free_kick.value += 1
                op_xg.goal.against.direct_free_kick.value += 1

        # Update direct kick off
        elif shot_type == "direct_kick_off":
            xg.xg.for_dir.direct_kick_off.value += xg_value
            op_xg.xg.against.direct_kick_off.value += xg_value
            xg.shot.for_dir.direct_kick_off.value += 1
            op_xg.shot.against.direct_kick_off.value += 1
            if is_on_target:
                xg.shot_target.for_dir.direct_kick_off.value += 1
                op_xg.shot_target.against.direct_kick_off.value += 1
            if is_goal:
                xg.goal.for_dir.direct_kick_off.value += 1
                op_xg.goal.against.direct_kick_off.value += 1

        # Update penalty
        elif shot_type == "penalty":
            xg.xg.for_dir.penalty.value += xg_value
            op_xg.xg.against.penalty.value += xg_value
            xg.shot.for_dir.penalty.value += 1
            op_xg.shot.against.penalty.value += 1
            if is_on_target:
                xg.shot_target.for_dir.penalty.value += 1
                op_xg.shot_target.against.penalty.value += 1
            if is_goal:
                xg.goal.for_dir.penalty.value += 1
                op_xg.goal.against.penalty.value += 1

        # Update open play
        elif shot_type == "open_play":
            xg.xg.for_dir.open_play.value += xg_value
            op_xg.xg.against.open_play.value += xg_value
            xg.shot.for_dir.open_play.value += 1
            op_xg.shot.against.open_play.value += 1
            if is_on_target:
                xg.shot_target.for_dir.open_play.value += 1
                op_xg.shot_target.against.open_play.value += 1
            if is_goal:
                xg.goal.for_dir.open_play.value += 1
                op_xg.goal.against.open_play.value += 1

        # Update set piece free kick
        elif shot_type == "set_piece_free_kick":
            xg.xg.for_dir.set_piece_free_kick.value += xg_value
            op_xg.xg.against.set_piece_free_kick.value += xg_value
            xg.shot.for_dir.set_piece_free_kick.value += 1
            op_xg.shot.against.set_piece_free_kick.value += 1
            if is_on_target:
                xg.shot_target.for_dir.set_piece_free_kick.value += 1
                op_xg.shot_target.against.set_piece_free_kick.value += 1
            if is_goal:
                xg.goal.for_dir.set_piece_free_kick.value += 1
                op_xg.goal.against.set_piece_free_kick.value += 1

        elif shot_type == "set_piece_corner":
            xg.xg.for_dir.set_piece_corner.value += xg_value
            op_xg.xg.against.set_piece_corner.value += xg_value
            xg.shot.for_dir.set_piece_corner.value += 1
            op_xg.shot.against.set_piece_corner.value += 1
            if is_on_target:
                xg.shot_target.for_dir.set_piece_corner.value += 1
                op_xg.shot_target.against.set_piece_corner.value += 1
            if is_goal:
                xg.goal.for_dir.set_piece_corner.value += 1
                op_xg.goal.against.set_piece_corner.value += 1

        elif shot_type == "set_piece_throw_in":
            xg.xg.for_dir.set_piece_throw_in.value += xg_value
            op_xg.xg.against.set_piece_throw_in.value += xg_value
            xg.shot.for_dir.set_piece_throw_in.value += 1
            op_xg.shot.against.set_piece_throw_in.value += 1
            if is_on_target:
                xg.shot_target.for_dir.set_piece_throw_in.value += 1
                op_xg.shot_target.against.set_piece_throw_in.value += 1
            if is_goal:
                xg.goal.for_dir.set_piece_throw_in.value += 1
                op_xg.goal.against.set_piece_throw_in.value += 1

        if "set_piece" in shot_type:
            xg.xg.for_dir.set_piece_total.value += xg_value
            op_xg.xg.against.set_piece_total.value += xg_value
            xg.shot.for_dir.set_piece_total.value += 1
            op_xg.shot.against.set_piece_total.value += 1
            if is_on_target:
                xg.shot_target.for_dir.set_piece_total.value += 1
                op_xg.shot_target.against.set_piece_total.value += 1
            if is_goal:
                xg.goal.for_dir.set_piece_total.value += 1
                op_xg.goal.against.set_piece_total.value += 1


    def _is_shot_event(self, event_row: Dict) -> bool:
        """Check if event is a shot."""
        if "type" not in event_row:
            return False

        event_type = event_row["type"]
        if isinstance(event_type, dict):
            return event_type.get("name") == "Shot"

        return event_type == "Shot"

    def _is_own_goal_event(self, event_row: Dict) -> bool:
            """Check if event is a shot."""
            if "type" not in event_row:
                return False
    
            event_type = event_row["type"]
            if isinstance(event_type, dict):
                return event_type.get("name") == "Own Goal For"
    
            return False

    def _get_team_id(self, event_row: Dict) -> Optional[int]:
        """Extract team ID from event."""
        if "team" in event_row and isinstance(event_row["team"], dict):
            return event_row["team"].get("id")
        return None
    
    def _get_xg_value(self, event_row: Dict) -> Optional[float]:
        """Extract xG value from shot event."""
        shot_data = event_row["shot"]
        xg = shot_data.get("statsbomb_xg")
        if xg is not None:
            try:
                return float(xg)
            except (ValueError, TypeError):
                return None
        return None

    def _get_xg_shot_uplift_value(self, event_row: Dict) -> Optional[float]:
        """Extract xG shot uplift value from shot event."""
        shot_data = event_row["shot"]
        xg = shot_data.get("shot_execution_xg_uplift")
        if xg is not None:
            try:
                return float(xg)
            except (ValueError, TypeError):
                return None
        return None
    
    def _is_goal(self, event_row: Dict) -> bool:
        """Check if shot resulted in a goal."""
        shot_data = event_row["shot"]
        outcome = shot_data.get("outcome")
        if isinstance(outcome, dict):
            return outcome.get("name") == "Goal"
        return outcome == "Goal"

    def _is_on_target(self, event_row: Dict) -> bool:
        """Check if shot was on target."""
        shot_data = event_row["shot"]
        outcome = shot_data.get("outcome")
        if isinstance(outcome, dict):
            outcome_name = outcome.get("name", "").lower()
        else:
            outcome_name = str(outcome).lower() if outcome else ""
        return outcome_name in ["goal", "saved", "saved off t", "saved to post", "post"]

    def _get_shot_type(self, event_row: Dict) -> str:
        """
        Extract shot type categorized as:
        - direct_corner, direct_free_kick, direct_kick_off, penalty
        - set_piece_corner, set_piece_throw_in, set_piece_free_kick
        - open_play
        """
        shot_data = event_row["shot"]
        shot_type = shot_data.get("type")
        if isinstance(shot_type, dict):
            shot_type_name = shot_type.get("name", "")
        else:
            shot_type_name = str(shot_type) if shot_type else ""

        # Direct shot types
        if shot_type_name == "Corner":
            return "direct_corner"
        elif shot_type_name == "Free Kick":
            return "direct_free_kick"
        elif shot_type_name == "Kick Off":
            return "direct_kick_off"
        elif shot_type_name == "Penalty":
            return "penalty"
        elif shot_type_name == "Open Play":
            # Check if set_piece_phase exists
            if "set_piece_phase" not in event_row:
                return "open_play"

            # set_piece_phase exists, check play_pattern
            play_pattern = self._get_play_pattern(event_row)
            if play_pattern == "from free kick":
                return "set_piece_free_kick"
            elif play_pattern == "from corner":
                return "set_piece_corner"
            elif play_pattern == "from throw in":
                return "set_piece_throw_in"
            else:
                return "open_play"

        return "open_play"

    def _get_body_part(self, event_row: Dict) -> str:
        """Extract body part used for shot (Head, Right Foot, Left Foot)."""
        shot_data = event_row["shot"]
        body_part = shot_data.get("body_part")
        if isinstance(body_part, dict):
            return body_part.get("name", "unknown")
        return str(body_part) if body_part else "unknown"

    def _is_one_on_one(self, event_row: Dict) -> bool:
        """Check if shot was a one-on-one situation."""
        shot_data = event_row["shot"]
        return shot_data.get("one_on_one", False)

    def _is_set_piece(self, event_row: Dict) -> bool:
        if "set_pieces_phase" not in event_row:
            return False
        else:
            return True
        
    def _get_shot_location(self, event_row: Dict) -> str:
        """
        Determine shot location (inbox or outbox).
        Assumes x coordinate: inbox = x > 102, outbox = x <= 102
        """
        if "location" not in event_row:
            return "unknown"

        location = event_row["location"]
        if not isinstance(location, (list, tuple)) or len(location) < 1:
            return "unknown"

        x_coord = location[0]
        y_coord = location[1]
        if x_coord >= 102:
            if (y_coord >= 18) and (y_coord <= 62):
                return "inbox"

        return "outbox"

    def _get_play_pattern(self, event_row: Dict) -> str:
        """Extract play pattern name (e.g., 'From Corner', 'From Throw In')."""
        if "play_pattern" not in event_row:
            return "unknown"

        play_pattern = event_row["play_pattern"]
        if isinstance(play_pattern, dict):
            pattern_name = play_pattern.get("name", "unknown")
        else:
            pattern_name = str(play_pattern) if play_pattern else "unknown"

        return pattern_name.lower()

    def initialize_team_aggregate(self, team_id: int, team_name: str) -> Dict:
        """Initialize aggregate structure for a team from multi-dimensional XGField."""
        aggregate = {'team_name': team_name, 'matches': 0}
        # Initialize metrics using backward compatibility keys
        xg_field = XGField()
        all_metrics = xg_field.get_all_metrics()
        for key in all_metrics:
            aggregate[key] = Metric.default()
        return aggregate

    def aggregate(self, team_aggregates: Dict, team_id: int, match_data: Dict) -> None:
        """
        Add a team's match xG data to the aggregate.

        Args:
            team_aggregates: Dictionary to accumulate stats
            team_id: Team ID
            match_data: Team data from single match (contains 'xg' key)
        """
        if team_id not in team_aggregates:
            team_aggregates[team_id] = self.initialize_team_aggregate(
                team_id, match_data.get('team_name', 'Unknown')
            )

        xg = match_data.get('xg')
        if not xg:
            return

        team_aggregates[team_id]['matches'] += 1
        # Get flattened metrics from the multi-dimensional structure
        all_metrics = xg.get_all_metrics()
        for key, metric in all_metrics.items():
            if isinstance(metric, Metric) and key in team_aggregates[team_id]:
                agg_metric = team_aggregates[team_id][key]
                agg_metric.value += metric.value

                # Append metric value to trend history
                if agg_metric.value_trend is None:
                    agg_metric.value_trend = []
                agg_metric.value_trend.append(metric.value)
