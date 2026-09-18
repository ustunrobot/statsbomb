#!/usr/bin/env python3
"""Insights engine: Generates varied, evidence-based insights from team metrics."""

import random
import copy
from typing import Dict, List, Tuple, Optional


class InsightGenerator:
    """Generate varied insights from team metrics with evidence."""

    THRESHOLDS = [2.0, 1.5, 1.0, 0.5]

    def __init__(self, team_metrics: dict, league_table: dict = None, team_name: str = "", statsbomb_team_metrics: dict = None):
        self.team_metrics = team_metrics
        self.league_table = league_table
        self.team_name = team_name
        self.statsbomb_team_metrics = statsbomb_team_metrics or {}        
        self.thresholds = self.THRESHOLDS        

    def _get_metric(self, metric_key: str):
        """Get metric from either event-based or StatsBomb metrics."""
        # First try event-based metrics
        metric = self.team_metrics.get(metric_key)
        if metric:
            return metric

        # Try StatsBomb metrics with team_season_ prefix
        sb_key = f"team_season_{metric_key}" if not metric_key.startswith("team_season_") else metric_key
        metric = self.statsbomb_team_metrics.get(self.team_name, {}).get(sb_key) if self.team_name else None
        return metric

    def convert_to_message(self, selected_metrics: List[Dict]) -> List:
        """Convert metrics to concise insight messages using z-score levels and random wording."""

        # Z-score level definitions with synonyms
        z_score_levels = {
            "excellent": {
                "range": (2.0, float('inf')),
                "adjectives": ["Excellent", "Outstanding", "Superb", "Elite", "Phenomenal"]
            },
            "very_good": {
                "range": (1.5, 2.0),
                "adjectives": ["Very Good", "Exceptional", "Superior", "Impressive", "Stellar"]
            },
            "good": {
                "range": (1.0, 1.5),
                "adjectives": ["Good", "Solid", "Strong", "Effective", "Proficient"]
            },
            "above_average": {
                "range": (0.5, 1.0),
                "adjectives": ["Above Average", "Competent", "Capable", "Respectable", "Decent"]
            },
            "average": {
                "range": (-0.5, 0.5),
                "adjectives": ["Average", "Moderate", "Standard", "Typical", "Balanced"]
            },
            "below_average": {
                "range": (-1.0, -0.5),
                "adjectives": ["Below Average", "Modest", "Limited", "Weak", "Subpar"]
            },
            "poor": {
                "range": (-1.5, -1.0),
                "adjectives": ["Poor", "Insufficient", "Inadequate", "Struggling", "Deficient"]
            },
            "very_poor": {
                "range": (-2.0, -1.5),
                "adjectives": ["Very Poor", "Very weak", "Very Inadequate", "Very Poor", "Very Insufficient"]
            },
            "exceptional_weakness": {
                "range": (float('-inf'), -2.0),
                "adjectives": ["Exceptional Weakness", "Critical Flaw", "Severe Deficit", "Major Weakness", "Fundamental Issue"]
            }
        }

        # Wording structure templates
        wording_templates = [
            "{label}: {adjective} {descriptor}",
            "Displays {adjective} {descriptor} in {label}",
            "{adjective} {descriptor} across {label}",
            "Shows {adjective} {descriptor} for {label}",
            "{label} stands as {adjective} {descriptor}",
            "{adjective} {descriptor} in {label}",                        
            "{label} demonstrates {adjective} {descriptor}",
            "{adjective} {descriptor} in their {label}"
        ]

        # Descriptors for context
        descriptors = ["performance", "level", "metric", "output", "execution", "capability"]

        messages = []
        for metric in selected_metrics:
            z_score = metric.get("z_score", 0)
            label = metric.get("label", "Metric")

            # Add value_pg (or value if value_pg is null) to label
            metric_obj = metric.get("metric")
            if metric_obj:
                value_to_show = getattr(metric_obj, 'value_pg', None) or getattr(metric_obj, 'value', None)
                if value_to_show is not None:
                    label = f"{label} ({value_to_show:.2f})"

            # Find appropriate level
            current_level = "average"
            for level_name, level_info in z_score_levels.items():
                range_min, range_max = level_info["range"]
                if range_min <= z_score < range_max:
                    current_level = level_name
                    break

            # Get adjective and wording
            level_info = z_score_levels[current_level]
            adjective = random.choice(level_info["adjectives"])
            descriptor = random.choice(descriptors)
            template = random.choice(wording_templates)

            # Format message
            message_text = template.format(
                label=label,
                adjective=adjective,
                descriptor=descriptor
            )
            
            messages.append(message_text)

        return messages

    def _generate_messages(self, metrics_list: List[Dict]) -> List:
        """Generate messages from metrics using thresholds.

        Returns 2 positive and 2 negative metrics based on z-scores and thresholds.
        """
        reversed_metrics = copy.deepcopy(metrics_list)

        # Loop through available metrics and filter valid ones
        for metric_entry in reversed_metrics:
            if not metric_entry.get("metric"):
                continue

            # Reverse z_score if reverse field is True
            metric_obj = metric_entry.get("metric")
            metric_reverse = metric_entry.get("reverse")
            #print(metric_obj, metric_entry.get(""))
            if metric_obj and metric_reverse:                
                metric_obj.z_score = getattr(metric_obj, 'z_score', 0) * -1
                
        positive_metrics = []
        negative_metrics = []
        used_indices = set()

        # Find 2 positive metrics
        for _ in range(2):
            positive = self._find_best_positive_metric(reversed_metrics, used_indices)
            if positive:
                positive_metrics.append(positive)
                used_indices.add(positive["index"])

        # Find 2 negative metrics
        for _ in range(2):
            negative = self._find_best_negative_metric(reversed_metrics, used_indices)
            if negative:
                negative_metrics.append(negative)
                used_indices.add(negative["index"])

        # Return all 4 metrics in metrics_list format (preserving all fields)
        selected_metrics = positive_metrics + negative_metrics
        selected_messages = self.convert_to_message(selected_metrics)  # Convert to message format
        return selected_messages

    def _find_best_positive_metric(self, metrics_list: List[Dict], used_indices: set) -> Dict:
        """Find the best positive metric based on z-score and thresholds."""
        # Level 3 threshold (highest requirement)
        level_3_threshold = self.thresholds[2]  # 1.0
        level_2_threshold = self.thresholds[1]  # 1.5

        # Step 1: Find highest z-score primary metric >= level_3_threshold
        primary_metrics = [(i, m) for i, m in enumerate(metrics_list)
                          if m["type"] == "primary" and i not in used_indices and m["metric"]]

        if primary_metrics:
            best_primary = max(primary_metrics, key=lambda x: x[1]["metric"].z_score if hasattr(x[1]["metric"], 'z_score') else -float('inf'))
            if best_primary[1]["metric"].z_score >= level_3_threshold:
                result = best_primary[1].copy()
                result["index"] = best_primary[0]
                result["z_score"] = best_primary[1]["metric"].z_score
                result["level"] = "level_3"
                return result

        # Step 2: Find highest z-score secondary metric >= level_2_threshold
        secondary_metrics = [(i, m) for i, m in enumerate(metrics_list)
                            if m["type"] == "secondary" and i not in used_indices and m["metric"]]

        if secondary_metrics:
            best_secondary = max(secondary_metrics, key=lambda x: x[1]["metric"].z_score if hasattr(x[1]["metric"], 'z_score') else -float('inf'))
            if best_secondary[1]["metric"].z_score >= level_2_threshold:
                result = best_secondary[1].copy()
                result["index"] = best_secondary[0]
                result["z_score"] = best_secondary[1]["metric"].z_score
                result["level"] = "level_2"
                return result

        # Step 3: Take highest z-score from all remaining metrics
        all_metrics = [(i, m) for i, m in enumerate(metrics_list)
                       if i not in used_indices and m["metric"]]

        if all_metrics:
            best = max(all_metrics, key=lambda x: x[1]["metric"].z_score if hasattr(x[1]["metric"], 'z_score') else -float('inf'))
            result = best[1].copy()
            result["index"] = best[0]
            result["z_score"] = best[1]["metric"].z_score
            result["level"] = "other"
            return result

        return None

    def _find_best_negative_metric(self, metrics_list: List[Dict], used_indices: set) -> Dict:
        """Find the best negative metric based on z-score and thresholds."""
        # Level 3 threshold (highest requirement) - use negative
        level_3_threshold = -self.thresholds[2]  # -1.0
        level_2_threshold = -self.thresholds[1]  # -1.5

        # Step 1: Find lowest z-score primary metric <= level_3_threshold
        primary_metrics = [(i, m) for i, m in enumerate(metrics_list)
                          if m["type"] == "primary" and i not in used_indices and m["metric"]]

        if primary_metrics:
            best_primary = min(primary_metrics, key=lambda x: x[1]["metric"].z_score if hasattr(x[1]["metric"], 'z_score') else float('inf'))
            if best_primary[1]["metric"].z_score <= level_3_threshold:
                result = best_primary[1].copy()
                result["index"] = best_primary[0]
                result["z_score"] = best_primary[1]["metric"].z_score
                result["level"] = "level_3"
                return result

        # Step 2: Find lowest z-score secondary metric <= level_2_threshold
        secondary_metrics = [(i, m) for i, m in enumerate(metrics_list)
                            if m["type"] == "secondary" and i not in used_indices and m["metric"]]

        if secondary_metrics:
            best_secondary = min(secondary_metrics, key=lambda x: x[1]["metric"].z_score if hasattr(x[1]["metric"], 'z_score') else float('inf'))
            if best_secondary[1]["metric"].z_score <= level_2_threshold:
                result = best_secondary[1].copy()
                result["index"] = best_secondary[0]
                result["z_score"] = best_secondary[1]["metric"].z_score
                result["level"] = "level_2"
                return result

        # Step 3: Take lowest z-score from all remaining metrics
        all_metrics = [(i, m) for i, m in enumerate(metrics_list)
                       if i not in used_indices and m["metric"]]

        if all_metrics:
            best = min(all_metrics, key=lambda x: x[1]["metric"].z_score if hasattr(x[1]["metric"], 'z_score') else float('inf'))
            result = best[1].copy()
            result["index"] = best[0]
            result["z_score"] = best[1]["metric"].z_score
            result["level"] = "other"
            return result

        return None
             
    def generate_possession_insights(self) -> List:
        metrics_list = [
            {"metric": self._get_metric("team_season_possession"), "type": "primary", "label": "Possession %", "reverse": False},
            {"metric": self._get_metric("team_season_directness"), "type": "primary", "label": "Directness", "reverse": False},
            {"metric": self._get_metric("team_season_passing_ratio"), "type": "primary", "label": "Pass Completion", "reverse": False},
            {"metric": self._get_metric("team_season_obv_pg"), "type": "secondary", "label": "On Ball Value created", "reverse": False},
            {"metric": self._get_metric("team_season_total_dribbles_pg"), "type": "primary", "label": "Dribbles per game", "reverse": False},
            {"metric": self._get_metric("carry_x_distance_total"), "type": "secondary", "label": "Vertical Carries", "reverse": False},
            {"metric": self._get_metric("aerial_won_ratio"), "type": "primary", "label": "Aerial win ratio", "reverse": False},
            {"metric": self._get_metric("aerial_total"), "type": "primary", "label": "Total Aerials", "reverse": False},
            {"metric": self._get_metric("team_season_corners_pg"), "type": "secondary", "label": "Corners per Game", "reverse": False},
            {"metric": self._get_metric("team_season_ball_in_play_time"), "type": "secondary", "label": "Ball in play time", "reverse": False},
            {"metric": self._get_metric("team_season_completed_dribbles_pg"), "type": "secondary", "label": "Completed dribbles per game", "reverse": False},               
        ]                
        attack_messages = self._generate_messages(metrics_list)
        
        return attack_messages

    
    def generate_attacking_insights(self) -> List:
        """Generate attacking insights: Strength, Concern"""
        
        metrics_list = [
            {"metric": self._get_metric("xg_for_total"), "type": "primary", "label": "xG For", "reverse": False},
            {"metric": self._get_metric("shot_for_total"), "type": "primary", "label": "Shots", "reverse": False},
            {"metric": self._get_metric("goal_for_total"), "type": "primary", "label": "Goals", "reverse": False},
            {"metric": self._get_metric("goal_per_xgf"), "type": "primary", "label": "Finishing", "reverse": False},
            {"metric": self._get_metric("xgf_per_shot"), "type": "primary", "label": "xG/Shot", "reverse": False},
            {"metric": self._get_metric("xgf_set_piece_ratio"), "type": "primary", "label": "Set Piece %", "reverse": False},
            {"metric": self._get_metric("xg_for_header"), "type": "primary", "label": "Header xG", "reverse": False},
            {"metric": self._get_metric("team_season_xgd"), "type": "primary", "label": "xG Diff", "reverse": False},
            {"metric": self._get_metric("team_season_np_xg_pg"), "type": "primary", "label": "Non-Pen xG", "reverse": False},            
            {"metric": self._get_metric("team_season_counter_attacking_shots_pg"), "type": "secondary", "label": "Counter Attack Shots", "reverse": False},
            {"metric": self._get_metric("team_season_crosses_into_box_pg"), "type": "secondary", "label": "Crosses into Box", "reverse": False}, 
            {"metric": self._get_metric("team_season_transition_xg_pg"), "type": "secondary", "label": "Transition xG", "reverse": False},
            {"metric": self._get_metric("team_season_corner_xg_pg"), "type": "secondary", "label": "Corner xG", "reverse": False}
            
        ]
        
        attack_messages = self._generate_messages(metrics_list)
        
        return attack_messages

    
    def generate_defense_insights(self) -> List:
         metrics_list = [
            {"metric": self._get_metric("xg_against_total"), "type": "primary", "label": "xG Conceded", "reverse": True},
            {"metric": self._get_metric("shot_against_total"), "type": "primary", "label": "Shots Conceded", "reverse": True},
            {"metric": self._get_metric("goal_against_total"), "type": "primary", "label": "Goals Conceded", "reverse": True},
            {"metric": self._get_metric("xg_against_header"), "type": "primary", "label": "Header xG Conceeded", "reverse": True},
            {"metric": self._get_metric("xg_against_set_piece_total"), "type": "primary", "label": "xG conceeded from set pieces", "reverse": True},
            {"metric": self._get_metric("team_season_counterpressure_regains_pg"), "type": "primary", "label": "Counter press regains per game", "reverse": False},
            {"metric": self._get_metric("team_season_pressures_pg"), "type": "primary", "label": "Pressures per game", "reverse": False},
            {"metric": self._get_metric("team_season_pressure_regains_pg"), "type": "primary", "label": "Pressure regains per game", "reverse": False},            
        ]
                
         attack_messages = self._generate_messages(metrics_list)
        
         return attack_messages
        

    