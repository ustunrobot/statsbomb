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

from typing import Dict, Optional
from dataclasses import dataclass, field as dataclass_field, fields
from ..metrics import Metric


@dataclass
class XGField:
    """Accumulated xG metrics for a team in a match (each field is a Metric)."""
    xgf: Metric = dataclass_field(default_factory=Metric.default)
    xgf_penalty: Metric = dataclass_field(default_factory=Metric.default)
    xgf_open_play: Metric = dataclass_field(default_factory=Metric.default)
    xgf_open_play_inbox: Metric = dataclass_field(default_factory=Metric.default)
    xgf_open_play_outbox: Metric = dataclass_field(default_factory=Metric.default)
    xgf_corner: Metric = dataclass_field(default_factory=Metric.default)
    xgf_from_corner: Metric = dataclass_field(default_factory=Metric.default)
    xgf_from_throw_in: Metric = dataclass_field(default_factory=Metric.default)
    xgf_free_kick: Metric = dataclass_field(default_factory=Metric.default)
    xga: Metric = dataclass_field(default_factory=Metric.default)
    xga_penalty: Metric = dataclass_field(default_factory=Metric.default)
    xga_open_play: Metric = dataclass_field(default_factory=Metric.default)
    xga_open_play_inbox: Metric = dataclass_field(default_factory=Metric.default)
    xga_open_play_outbox: Metric = dataclass_field(default_factory=Metric.default)
    xga_corner: Metric = dataclass_field(default_factory=Metric.default)
    xga_from_corner: Metric = dataclass_field(default_factory=Metric.default)
    xga_from_throw_in: Metric = dataclass_field(default_factory=Metric.default)
    xga_free_kick: Metric = dataclass_field(default_factory=Metric.default)
    goals: Metric = dataclass_field(default_factory=Metric.default)
    goals_penalty: Metric = dataclass_field(default_factory=Metric.default)
    goals_open_play: Metric = dataclass_field(default_factory=Metric.default)
    goals_corner: Metric = dataclass_field(default_factory=Metric.default)
    goals_free_kick: Metric = dataclass_field(default_factory=Metric.default)
    goals_headers: Metric = dataclass_field(default_factory=Metric.default)
    goals_conceded: Metric = dataclass_field(default_factory=Metric.default)
    goals_conceded_penalty: Metric = dataclass_field(default_factory=Metric.default)
    goals_conceded_open_play: Metric = dataclass_field(default_factory=Metric.default)
    goals_conceded_corner: Metric = dataclass_field(default_factory=Metric.default)
    goals_conceded_free_kick: Metric = dataclass_field(default_factory=Metric.default)
    goals_conceded_headers: Metric = dataclass_field(default_factory=Metric.default)
    shots: Metric = dataclass_field(default_factory=Metric.default)
    shots_penalty: Metric = dataclass_field(default_factory=Metric.default)
    shots_open_play: Metric = dataclass_field(default_factory=Metric.default)
    shots_open_play_inbox: Metric = dataclass_field(default_factory=Metric.default)
    shots_open_play_outbox: Metric = dataclass_field(default_factory=Metric.default)
    shots_corner: Metric = dataclass_field(default_factory=Metric.default)
    shots_free_kick: Metric = dataclass_field(default_factory=Metric.default)
    shots_headers: Metric = dataclass_field(default_factory=Metric.default)
    op_shots: Metric = dataclass_field(default_factory=Metric.default)
    op_shots_penalty: Metric = dataclass_field(default_factory=Metric.default)
    op_shots_open_play: Metric = dataclass_field(default_factory=Metric.default)
    op_shots_open_play_inbox: Metric = dataclass_field(default_factory=Metric.default)
    op_shots_open_play_outbox: Metric = dataclass_field(default_factory=Metric.default)
    op_shots_corner: Metric = dataclass_field(default_factory=Metric.default)
    op_shots_free_kick: Metric = dataclass_field(default_factory=Metric.default)
    op_shots_headers: Metric = dataclass_field(default_factory=Metric.default)
    shots_on_target: Metric = dataclass_field(default_factory=Metric.default)
    op_shots_on_target: Metric = dataclass_field(default_factory=Metric.default)
    one_on_one_shots: Metric = dataclass_field(default_factory=Metric.default)
    op_one_on_one_shots: Metric = dataclass_field(default_factory=Metric.default)
    xgf_open_play_shot_uplift: Metric = dataclass_field(default_factory=Metric.default)
    xgf_headers: Metric = dataclass_field(default_factory=Metric.default)
    xga_headers: Metric = dataclass_field(default_factory=Metric.default)
    xgf_vs_real: Metric = dataclass_field(default_factory=Metric.default)
    xga_vs_real: Metric = dataclass_field(default_factory=Metric.default)


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
        shot_location = self._get_shot_location(event_row)
        play_pattern = self._get_play_pattern(event_row)

        # Update attacking team stats
        team["xg"].xgf.value += xg_value
        team["xg"].xgf_vs_real.value += xg_value
        team["xg"].shots.value += 1

        # Update defending team stats
        op_team["xg"].xga.value += xg_value
        op_team["xg"].xga_vs_real.value += xg_value
        op_team["xg"].op_shots.value += 1

        # On target tracking
        if self._is_on_target(event_row):
            team["xg"].shots_on_target.value += 1
            op_team["xg"].op_shots_on_target.value += 1

        # Categorize by shot type (Penalty, Free Kick, Corner, Open Play)
        if shot_type == "penalty":
            team["xg"].xgf_penalty.value += xg_value
            op_team["xg"].xga_penalty.value += xg_value
            team["xg"].shots_penalty.value += 1
            op_team["xg"].op_shots_penalty.value += 1
        elif shot_type == "free kick":
            team["xg"].xgf_free_kick.value += xg_value
            op_team["xg"].xga_free_kick.value += xg_value
            team["xg"].shots_free_kick.value += 1
            op_team["xg"].op_shots_free_kick.value += 1
        elif shot_type == "corner":
            team["xg"].xgf_corner.value += xg_value
            print ("corner xg:", xg_value)
            op_team["xg"].xga_corner.value += xg_value
            team["xg"].shots_corner.value += 1
            op_team["xg"].op_shots_corner.value += 1
        elif shot_type == "open play":
            team["xg"].xgf_open_play.value += xg_value
            op_team["xg"].xga_open_play.value += xg_value
            team["xg"].shots_open_play.value += 1
            op_team["xg"].op_shots_open_play.value += 1
            team["xg"].xgf_open_play_shot_uplift.value += xg_shot_uplift_value

            # Further categorize open play by location
            if shot_location == "inbox":
                team["xg"].xgf_open_play_inbox.value += xg_value
                op_team["xg"].xga_open_play_inbox.value += xg_value
                team["xg"].shots_open_play_inbox.value += 1
                op_team["xg"].op_shots_open_play_inbox.value += 1
            elif shot_location == "outbox":
                team["xg"].xgf_open_play_outbox.value += xg_value
                op_team["xg"].xga_open_play_outbox.value += xg_value
                team["xg"].shots_open_play_outbox.value += 1
                op_team["xg"].op_shots_open_play_outbox.value += 1

        # Body part tracking (headers)
        if is_header:
            team["xg"].shots_headers.value += 1
            op_team["xg"].op_shots_headers.value += 1
            team["xg"].xgf_headers.value += xg_value
            op_team["xg"].xga_headers.value += xg_value

        # Play pattern tracking (corners and throw-ins)
        if play_pattern == "from corner":
            team["xg"].xgf_from_corner.value += xg_value
            op_team["xg"].xga_from_corner.value += xg_value
        elif play_pattern == "from throw in":
            team["xg"].xgf_from_throw_in.value += xg_value
            op_team["xg"].xga_from_throw_in.value += xg_value

        # One-on-one tracking
        if is_one_on_one:
            team["xg"].one_on_one_shots.value += 1
            op_team["xg"].op_one_on_one_shots.value += 1

        # Track goals
        if is_goal:
            team["xg"].goals.value += 1
            team["xg"].xgf_vs_real.value -= 1
            op_team["xg"].goals_conceded.value += 1
            op_team["xg"].xga_vs_real.value -= 1

            # Categorize goals by type
            if shot_type == "penalty":
                team["xg"].goals_penalty.value += 1
                op_team["xg"].goals_conceded_penalty.value += 1
            elif shot_type == "free kick":
                team["xg"].goals_free_kick.value += 1
                op_team["xg"].goals_conceded_free_kick.value += 1
            elif shot_type == "corner":
                team["xg"].goals_corner.value += 1
                op_team["xg"].goals_conceded_corner.value += 1
            elif shot_type == "open play":
                team["xg"].goals_open_play.value += 1
                op_team["xg"].goals_conceded_open_play.value += 1

            # Goals by body part
            if is_header:
                team["xg"].goals_headers.value += 1
                op_team["xg"].goals_conceded_headers.value += 1

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
        """Initialize aggregate structure for a team (dynamically from XGField)."""
        aggregate = {'team_name': team_name, 'matches': 0}
        for field_info in fields(XGField):
            aggregate[field_info.name] = Metric.default()
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
        for field_info in fields(XGField):
            metric = getattr(xg, field_info.name, None)
            if isinstance(metric, Metric):
                team_aggregates[team_id][field_info.name].value += metric.value
