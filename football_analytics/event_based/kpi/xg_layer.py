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
             set_piece_total, open_play, header, foot, inbox, outbox

    Access: xg_field.xg.for.open_play or xg_field["xg"]["for"]["open_play"]
    """

    def __init__(self):
        # Define metric types
        self._metric_types = [
            'total', 'direct_corner', 'direct_free_kick', 'direct_kick_off',
            'penalty', 'set_piece_corner', 'set_piece_throw_in', 'set_piece_free_kick',
            'set_piece_total', 'open_play', 'header', 'foot', 'inbox', 'outbox', 'one_on_one'
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
    'xgf_minus_goal': {
            'description': 'Expected goals per shot',
            'type': 'total',
            'formula': lambda agg: agg['xg_for_total'].value - agg['goal_for_total'].value
        },
    'xga_minus_goal': {
                'description': 'Expected goals per shot',
                'type': 'total',
                'formula': lambda agg: agg['xg_against_total'].value - agg['goal_against_total'].value
            },
    'xgf_per_shot': {
        'description': 'Expected goals per shot',
        'type': 'ratio',
        'formula': lambda agg: agg['xg_for_total'].value / max(1, agg['shot_for_total'].value)
    },
    'xgf_open_play_per_open_shots': {
        'description': 'Expected goals per open play shot',
        'type': 'ratio',
        'formula': lambda agg: agg['xg_for_open_play'].value / max(1, agg['shot_for_open_play'].value)
    },
    'shots_outbox_per_shots': {
        'description': 'Outbox shot ratio in open play shots',
        'type': 'ratio',
        'formula': lambda agg: agg['shot_for_outbox'].value / max(1, agg['shot_for_open_play'].value)
    },
    'xgf_open_play_outbox_per_xgf': {
        'description': 'Outbox xGF ratio in open play xGF',
        'type': 'ratio',
        'formula': lambda agg: agg['xg_for_outbox'].value / max(1, agg['xg_for_open_play'].value)
    },
    'xgf_set_piece_ratio': {
        'description': 'Set piece xGF ratio in total xGF',
        'type': 'ratio',
        'formula': lambda agg: agg['xg_for_set_piece_total'].value / max(1, agg['xg_for_total'].value)
    },
    'xgf_open_play_ratio': {
        'description': 'Open play xGF ratio in total xGF',
        'type': 'ratio',
        'formula': lambda agg: agg['xg_for_open_play'].value / max(1, agg['xg_for_total'].value)
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
        # Only process shot events
        if not self._is_shot_event(event_row):
            return

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
        is_set_piece = self._is_set_piece(event_row)
        shot_location = self._get_shot_location(event_row)
        play_pattern = self._get_play_pattern(event_row)

        xg = team["xg"]
        op_xg = op_team["xg"]

        # Update attacking team stats - total
        xg.xg.for_dir.total.value += xg_value
        xg.shot.for_dir.total.value += 1

        # Update defending team stats - total
        op_xg.xg.against.total.value += xg_value
        op_xg.shot.against.total.value += 1

        # On target tracking
        if self._is_on_target(event_row):
            xg.shot_target.for_dir.total.value += 1
            op_xg.shot_target.against.total.value += 1

       ## BURALAR DÜZELECEK TEK TEK İNCELE YENİ DIMENSION BASED YAPIYA GÖRE
       ##  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1

        # Categorize by shot type (Penalty, Free Kick, Corner, Open Play)
        if shot_type == "penalty":
            xg.xg.for_dir.penalty.value += xg_value
            op_xg.xg.against.penalty.value += xg_value
            xg.shot.for_dir.penalty.value += 1
            op_xg.shot.against.penalty.value += 1
        elif shot_type == "free kick":
            xg.xg.for_dir.set_piece_free_kick.value += xg_value
            op_xg.xg.against.set_piece_free_kick.value += xg_value
            xg.shot.for_dir.set_piece_free_kick.value += 1
            op_xg.shot.against.set_piece_free_kick.value += 1
        elif shot_type == "corner":
            xg.xg.for_dir.set_piece_corner.value += xg_value
            op_xg.xg.against.set_piece_corner.value += xg_value
            xg.shot.for_dir.set_piece_corner.value += 1
            op_xg.shot.against.set_piece_corner.value += 1
        elif shot_type == "open play":
            xg.xg.for_dir.open_play.value += xg_value
            op_xg.xg.against.open_play.value += xg_value
            xg.shot.for_dir.open_play.value += 1
            op_xg.shot.against.open_play.value += 1

            # Further categorize open play by location
            if shot_location == "inbox":
                xg.xg.for_dir.inbox.value += xg_value
                op_xg.xg.against.inbox.value += xg_value
                xg.shot.for_dir.inbox.value += 1
                op_xg.shot.against.inbox.value += 1
            elif shot_location == "outbox":
                xg.xg.for_dir.outbox.value += xg_value
                op_xg.xg.against.outbox.value += xg_value
                xg.shot.for_dir.outbox.value += 1
                op_xg.shot.against.outbox.value += 1

        # Body part tracking (headers)
        if is_header:
            xg.shot.for_dir.header.value += 1
            op_xg.shot.against.header.value += 1
            xg.xg.for_dir.header.value += xg_value
            op_xg.xg.against.header.value += xg_value

        # Play pattern tracking (corners and throw-ins)
        if play_pattern == "from corner":
            xg.xg.for_dir.set_piece_corner.value += xg_value
            op_xg.xg.against.set_piece_corner.value += xg_value
        elif play_pattern == "from throw in":
            xg.xg.for_dir.set_piece_throw_in.value += xg_value
            op_xg.xg.against.set_piece_throw_in.value += xg_value

        # One-on-one tracking (added to metric types if needed)
        if is_one_on_one:
            xg.shot.for_dir.one_on_one.value += 1
            op_xg.shot.against.one_on_one.value += 1

        if is_set_piece:
            xg.xg.for_dir.set_piece_total.value += xg_value
            op_xg.xg.against.set_piece_total.value += xg_value

        # Track goals
        if is_goal:
            xg.goal.for_dir.total.value += 1
            op_xg.goal.against.total.value += 1

            # Categorize goals by type
            if shot_type == "penalty":
                xg.goal.for_dir.penalty.value += 1
                op_xg.goal.against.penalty.value += 1
            elif shot_type == "free kick":
                xg.goal.for_dir.set_piece_free_kick.value += 1
                op_xg.goal.against.set_piece_free_kick.value += 1
            elif shot_type == "corner":
                xg.goal.for_dir.set_piece_corner.value += 1
                op_xg.goal.against.set_piece_corner.value += 1
            elif shot_type == "open play":
                xg.goal.for_dir.open_play.value += 1
                op_xg.goal.against.open_play.value += 1

            # Goals by body part
            if is_header:
                xg.goal.for_dir.header.value += 1
                op_xg.goal.against.header.value += 1

    def _is_shot_event(self, event_row: Dict) -> bool:
        """Check if event is a shot."""
        if "type" not in event_row:
            return False

        event_type = event_row["type"]
        if isinstance(event_type, dict):
            return event_type.get("name") == "Shot"

        return event_type == "Shot"

    def _get_team_id(self, event_row: Dict) -> Optional[int]:
        """Extract team ID from event."""
        if "team" in event_row and isinstance(event_row["team"], dict):
            return event_row["team"].get("id")
        return None

    def _get_xg_value(self, event_row: Dict) -> Optional[float]:
        """Extract xG value from shot event."""
        if "shot" not in event_row:
            return None

        shot_data = event_row["shot"]
        if not isinstance(shot_data, dict):
            return None

        # Try multiple xG field names (StatsBomb uses statsbomb_xg)
        xg = shot_data.get("statsbomb_xg") 
        if xg is not None:
            try:
                return float(xg)
            except (ValueError, TypeError):
                return None

        return None

    def _get_xg_shot_uplift_value(self, event_row: Dict) -> Optional[float]:
            """Extract xG value from shot event."""
            if "shot" not in event_row:
                return None
    
            shot_data = event_row["shot"]
            if not isinstance(shot_data, dict):
                return None
    
            # Try multiple xG field names (StatsBomb uses statsbomb_xg)
            xg = shot_data.get("shot_execution_xg_uplift") 
            if xg is not None:
                try:
                    return float(xg)
                except (ValueError, TypeError):
                    return None
    
            return None
    
    def _is_goal(self, event_row: Dict) -> bool:
        """Check if shot resulted in a goal."""
        if "shot" not in event_row:
            return False

        shot_data = event_row["shot"]
        if not isinstance(shot_data, dict):
            return False

        outcome = shot_data.get("outcome")
        if isinstance(outcome, dict):
            return outcome.get("name") == "Goal"

        return outcome == "Goal"

    def _is_on_target(self, event_row: Dict) -> bool:
        """Check if shot was on target."""
        if "shot" not in event_row:
            return False

        shot_data = event_row["shot"]
        if not isinstance(shot_data, dict):
            return False

        outcome = shot_data.get("outcome")
        if isinstance(outcome, dict):
            outcome_name = outcome.get("name", "").lower()
        else:
            outcome_name = str(outcome).lower() if outcome else ""

        return outcome_name in ["goal", "saved", "saved off t", "saved to post", "post"]

    def _get_shot_type(self, event_row: Dict) -> str:
        """Extract shot type (e.g., 'open_play', 'set_piece')."""
        if "shot" not in event_row:
            return "unknown"

        shot_data = event_row["shot"]
        if not isinstance(shot_data, dict):
            return "unknown"

        shot_type = shot_data.get("type")
        if isinstance(shot_type, dict):
            return shot_type.get("name", "unknown").lower()

        return str(shot_type).lower() if shot_type else "unknown"

    def _get_body_part(self, event_row: Dict) -> str:
        """Extract body part used for shot (Head, Right Foot, Left Foot)."""
        if "shot" not in event_row:
            return "unknown"

        shot_data = event_row["shot"]
        if not isinstance(shot_data, dict):
            return "unknown"

        body_part = shot_data.get("body_part")
        if isinstance(body_part, dict):
            return body_part.get("name", "unknown")

        return str(body_part) if body_part else "unknown"

    def _is_one_on_one(self, event_row: Dict) -> bool:
        """Check if shot was a one-on-one situation."""
        if "shot" not in event_row:
            return False

        shot_data = event_row["shot"]
        if not isinstance(shot_data, dict):
            return False

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
                team_aggregates[team_id][key].value += metric.value
