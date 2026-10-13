"""
Data Provider: Identifies and collects match event files for processing.

Responsibilities:
- Scan team directories for match event files
- Deduplicate files (same match exists in both team folders)
- Filter out 360frames files
- Load event data in chronological order
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime


class DataProvider:
    """Provides match event data for processing."""

    PLAYER_POSITIONS = {
        1: "Goalkeeper",
        2: "Right Back",
        3: "Right Centre Back",
        4: "Centre Back",
        5: "Left Centre Back",
        6: "Left Back",
        7: "Right Wing Back",
        8: "Left Wing Back",
        9: "Right Defensive Midfielder",
        10: "Centre Defensive Midfielder",
        11: "Left Defensive Midfielder",
        12: "Right Midfielder",
        13: "Right Centre Midfielder",
        14: "Centre Midfielder",
        15: "Left Centre Midfielder",
        16: "Left Midfielder",
        17: "Right Wing",
        18: "Right Attacking Midfielder",
        19: "Centre Attacking Midfielder",
        20: "Left Attacking Midfielder",
        21: "Left Wing",
        22: "Right Centre Forward",
        23: "Centre Forward",
        24: "Left Centre Forward",
    }

    POSITION_COMPARISON_SETS = {
        1: {1},
        2: {2, 3, 4, 5, 6, 7, 8, 9, 10, 11},
        3: {2, 3, 4, 5, 6, 7, 8, 9, 10, 11},
        4: {2, 3, 4, 5, 6, 7, 8, 9, 10, 11},
        5: {2, 3, 4, 5, 6, 7, 8, 9, 10, 11},
        6: {2, 3, 4, 5, 6, 7, 8, 9, 10, 11},
        7: {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 21, 17},
        8: {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 21, 17},
        9: {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16},
        10: {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16},
        11: {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16},
        12: {9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20},
        13: {9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20},
        14: {9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20},
        15: {9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20},
        16: {9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20},
        17: {7, 8, 17, 18, 19, 20, 21, 22, 24},
        18: {7, 8, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24},
        19: {7, 8, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24},
        20: {7, 8, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24},
        21: {17, 18, 19, 20, 21, 22, 24},
        22: {17, 18, 19, 20, 21, 22, 23, 24},
        23: {18, 19, 20, 22, 23, 24},
        24: {17, 18, 19, 20, 21, 22, 23, 24},
    }

    def __init__(self, data_root: str = None):
        if data_root is None:
            # Resolve data path relative to module location
            module_dir = Path(__file__).parent.parent
            data_root = module_dir / "data_temp" / "teams"
        self.data_root = Path(data_root)
        self.min_minutes_threshold = None  # Threshold for filtering players with very few minutes
        self._name_overrides = None  # Cache for manual StatsBomb<->SkillCorner name overrides

    def get_matches(
        self,
        seasons: List[str] = None,
        team_name: str = None,
        week_no: int = None,
    ) -> List[Tuple[str, Dict]]:
        """
        Collect and load match event files in chronological order.

        Args:
            seasons: List of season folders to include (e.g. ['25-26', '26-27']).
                    Defaults to ['25-26', '26-27'].
            team_name: Optional team name. Only takes effect when week_no is
                    also given: team_name's matches in every week other than
                    week_no are filtered out. Matches of all other teams are
                    left untouched.
            week_no: Optional week number. See team_name.

        Returns:
            List of tuples: (match_filename, event_data_dict)
            Ordered by week number, deduplicated.
        """
        if seasons is None:
            #seasons = ['25-26', '26-27']
            seasons = ['2026-2027']

        print(f"[DataProvider] Starting to collect match files for seasons: {seasons}", flush=True)

        # Collect all valid match files across all teams
        match_files = self._collect_match_files(seasons)
        print(f"[DataProvider] Found {len(match_files)} total match files across all teams", flush=True)

        # Deduplicate and sort by week
        unique_matches = self._deduplicate_and_sort(match_files)
        print(f"[DataProvider] After deduplication: {len(unique_matches)} unique matches", flush=True)

        # If both team_name and week_no are given, drop team_name's matches in
        # every other week - matches of all other teams are left untouched.
        if team_name is not None and week_no is not None:
            before_count = len(unique_matches)
            unique_matches = [
                match_path for match_path in unique_matches
                if team_name not in self._get_teams_from_filename(match_path.name)
                or self._get_week_from_filename(match_path.name) == week_no
            ]
            print(f"[DataProvider] Filtered {team_name} to week {week_no}: {before_count} -> {len(unique_matches)} matches", flush=True)

        # Load and return event data
        matches = []
        for i, match_filename in enumerate(unique_matches, 1):
            event_data = self._load_event_file(match_filename)
            if event_data:
                matches.append((match_filename, event_data))
                print(f"[DataProvider] Loaded match {i}/{len(unique_matches)}: {match_filename.name}", flush=True)
            else:
                print(f"[DataProvider] Failed to load match {i}/{len(unique_matches)}: {match_filename.name}", flush=True)

        print(f"[DataProvider] Successfully loaded {len(matches)}/{len(unique_matches)} matches", flush=True)
        return matches

    def get_team_weeks(self, team_name: str, season_name: str) -> List[Dict]:
        """
        List available match weeks for a team/season, based on already-downloaded
        event files in data_root/<team_name>/<season_folder>/.

        Args:
            team_name: Team name (matches the folder name under data_root)
            season_name: Season name, e.g. "2025/2026" (converted to the
                        "2025-2026" folder naming convention used on disk)

        Returns:
            List of dicts sorted by week number:
            {'week_no': int, 'filename': str, 'match_name': str}
        """
        season_folder = season_name.replace('/', '-')
        team_season_dir = self.data_root / team_name / season_folder

        print(f"[DataProvider] Looking for weeks in: {team_season_dir}")

        if not team_season_dir.exists():
            print(f"[DataProvider] Team season directory not found: {team_season_dir}")
            return []

        weeks = []
        for event_file in team_season_dir.glob("Week*.json"):
            if event_file.name.endswith("_360frames.json"):
                continue
            if event_file.name.endswith("_stats.json"):
                continue

            week_no = self._get_week_from_filename(event_file.name)
            home_team, away_team = self._get_teams_from_filename(event_file.name)

            weeks.append({
                'week_no': week_no,
                'filename': event_file.name,
                'match_name': f"Week {week_no}: {home_team} vs {away_team}",
            })

        weeks.sort(key=lambda w: w['week_no'])
        print(f"[DataProvider] Found {len(weeks)} weeks for {team_name} ({season_name})")
        return weeks

    def _collect_match_files(self, seasons: List[str]) -> List[Path]:
        """
        Scan all team directories and collect valid match event files.

        Filters:
        - Must be JSON
        - Must start with 'Week'
        - Must not end with '_360frames.json' or _stats.json

        Returns:
            List of Path objects to valid match files.
        """
        match_files = []

        if not self.data_root.exists():
            raise FileNotFoundError(f"Data root not found: {self.data_root}")

        print(f"[DataProvider] Scanning data root: {self.data_root}")
        print(f"[DataProvider] Looking for seasons: {seasons}")

        # Iterate through all team directories
        for team_dir in sorted(self.data_root.iterdir()):
            if not team_dir.is_dir():
                continue

            # Iterate through each season folder
            for season_folder in team_dir.iterdir():
                if not season_folder.is_dir():
                    continue

                # Check if this is one of the requested seasons
                if season_folder.name not in seasons:
                    continue

                print(f"[DataProvider] Checking season folder: {season_folder}")

                # Collect valid match files
                for event_file in season_folder.glob("Week*.json"):
                    # Skip 360frames files
                    if event_file.name.endswith("_360frames.json"):
                        continue
                    if event_file.name.endswith("_stats.json"):
                                            continue

                    print(f"[DataProvider] Found match file: {event_file.name}")
                    match_files.append(event_file)

        return match_files

    def _deduplicate_and_sort(self, match_files: List[Path]) -> List[Path]:
        """
        Deduplicate matches (same filename = same match) and sort by week.

        Args:
            match_files: List of Path objects to match files.

        Returns:
            Sorted list of deduplicated Path objects.
        """
        seen_filenames = {}

        for file_path in match_files:
            filename = file_path.name
            if filename not in seen_filenames:
                seen_filenames[filename] = file_path

        # Sort by week number extracted from filename
        sorted_matches = sorted(seen_filenames.values(), key=lambda path: self._get_week_from_filename(path.name))
        return sorted_matches

    @staticmethod
    def _get_week_from_filename(filename: str) -> int:
        """Extract week number from a match filename, e.g. 'Week10' from 'Week10_Barnet_vs_Accrington Stanley.json'."""
        week_str = filename.split('_')[0].replace('Week', '')
        try:
            return int(week_str)
        except ValueError:
            return 999  # Put unparseable files at the end

    @staticmethod
    def _get_teams_from_filename(filename: str) -> Tuple[str, str]:
        """Extract (home_team, away_team) from a match filename, e.g. ('Barnet', 'Accrington Stanley') from 'Week10_Barnet_vs_Accrington Stanley.json'."""
        name_without_ext = filename[:-5] if filename.endswith('.json') else filename
        parts = name_without_ext.split('_vs_')
        if len(parts) != 2:
            return ('', '')

        home_part, away_part = parts
        # home_part is like 'Week10_Barnet' - strip the 'WeekN_' prefix
        home_team = home_part.split('_', 1)[1] if '_' in home_part else home_part
        return (home_team, away_part)

    def _load_event_file(self, file_path: Path) -> Dict:
        """
        Load a single event file as a dictionary.

        Args:
            file_path: Path to the event JSON file.

        Returns:
            Dictionary of event data, or None if load fails.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading event file {file_path}: {e}")
            return None

    def process_player_stats(self, stats, player_id: int, match_stats: Dict = None) -> Dict:
        """
        Process player statistics and calculate percentiles and z-scores.
        Only compares against players in similar positions using POSITION_COMPARISON_SETS.

        Args:
            stats: List or dict from player_stats.json file
            player_id: ID of the player to process
            match_stats: Optional dict of player_id's match-level stats (one entry
                from a Week{N}_..._player_stats.json file). When given, player_id's
                entry is overridden in place (each player_season_* value replaced
                with its match-level equivalent - player_season_ -> player_match_,
                dropping a trailing '_90', or 0 if no equivalent is found) before
                any percentile/z-score comparisons run, so this player's displayed
                value and its rank among comparable players stay consistent.

        Returns:
            Dictionary with Metric objects for the given player, keyed by player_season_* metric names
        """
        from .metrics import Metric

        # Handle both list and dict structures
        if isinstance(stats, list):
            stats_list = stats
        else:
            stats_list = list(stats.values()) if isinstance(stats, dict) else []

        # Find the player data by player_id
        player_data = None
        for player_stats in stats_list:
            if isinstance(player_stats, dict) and player_stats.get('player_id') == player_id:
                player_data = player_stats
                break

        if not player_data:
            print(f"[DataProvider] Player ID '{player_id}' not found in stats")
            return {}
        else:
            print(f"{player_id} found. Name: {player_data.get('player_name')} primary: -{player_data.get('primary_position')}-")

        if match_stats is not None:
            # Build an overridden copy of this player's entry with match-level values
            # (player_season_* -> player_match_*, dropping a trailing '_90'), and swap
            # it into stats_list in place of the season-level entry. This keeps the
            # percentile/rank comparisons below consistent with the value being
            # displayed for this player - otherwise player_value (overridden) would
            # never be found among the comparison values (still season-level, pulled
            # from this same unmodified entry), making .index() always fail and the
            # rank always fall back to last place regardless of the actual z-score.
            overridden_player_data = dict(player_data)
            for key, value in player_data.items():
                if key.startswith('player_season_') and isinstance(value, (int, float)):
                    match_key = 'player_match_' + key[len('player_season_'):]
                    if match_key.endswith('_90'):
                        match_key = match_key[:-len('_90')]
                    overridden_player_data[key] = match_stats.get(match_key, 0)

            stats_list = [
                overridden_player_data if isinstance(p, dict) and p.get('player_id') == player_id else p
                for p in stats_list
            ]
            player_data = overridden_player_data

        # Get player position from primary_position field and find corresponding ID
        player_position_text = player_data.get('primary_position')
        player_position_id = None
        for pos_id, pos_name in self.PLAYER_POSITIONS.items():
            if pos_name == player_position_text:
                player_position_id = pos_id
                break

        if player_position_id is None:
            print(f"[DataProvider] Position '{player_position_text}' not found in PLAYER_POSITIONS")
            return {}

        comparison_positions = self.POSITION_COMPARISON_SETS.get(player_position_id, {player_position_id})

        # Convert position IDs back to position names for filtering
        comparable_position_names = {
            self.PLAYER_POSITIONS.get(pos_id) for pos_id in comparison_positions
        }

        # Filter stats_list to only include players with comparable positions
        filtered_stats_list = [
            p for p in stats_list
            if isinstance(p, dict) and p.get('primary_position') in comparable_position_names
        ]

        # Filter out players with very few minutes (z-score < -1.0), except the player being analyzed
        minutes_played = []
        for player in filtered_stats_list:
            minutes = player.get('player_season_minutes')
            if isinstance(minutes, (int, float)) and minutes > 0:
                minutes_played.append(minutes)

        if minutes_played and len(minutes_played) > 1:
            mean_minutes = sum(minutes_played) / len(minutes_played)
            variance = sum((x - mean_minutes) ** 2 for x in minutes_played) / len(minutes_played)
            std_dev = variance ** 0.5

            # Calculate threshold for z-score = -1.0
            minutes_threshold = mean_minutes - (0.6 * std_dev) if std_dev > 0 else 0
            self.min_minutes_threshold = minutes_threshold

            # Filter players by minimum minutes threshold, but always keep the player being analyzed
            filtered_stats_list = [
                p for p in filtered_stats_list
                if p.get('player_season_minutes', 0) >= minutes_threshold or p.get('player_id') == player_id
            ]

        # Use filtered list for sample size
        sample_size = len(filtered_stats_list)
        player_name = player_data.get('player_name', f'Player {player_id}')
        player_position_name = self.PLAYER_POSITIONS.get(player_position_id, f'Position {player_position_id}')
        print(f"[DataProvider] Processing stats for {player_name} (ID: {player_id}), position: {player_position_name}, sample_size: {sample_size}")

        # Extract all player_season_* metrics for this player
        player_metrics = {}
        for key, value in player_data.items():
            if key.startswith('player_season_') and isinstance(value, (int, float)):
                player_metrics[key] = value

        print(f"[DataProvider] Found {len(player_metrics)} metrics for {player_name}")

        # Calculate player age from birth_date
        birth_date = player_data.get('birth_date', '')
        player_age = None
        if birth_date and len(birth_date) >= 4:
            try:
                birth_year = int(birth_date[:4])
                current_year = datetime.now().year
                player_age = current_year - birth_year
            except ValueError:
                pass

        # Extract player metadata
        result = {
            'player_id': player_id,
            'player_name': player_name,
            'player_height': player_data.get('player_height'),
            'player_weight': player_data.get('player_weight'),
            'player_age': player_age,
            'player_position': player_position_text,
            'sample_size': sample_size,
            'minutes_threshold': self.min_minutes_threshold
        }

        for metric_key, player_value in player_metrics.items():
            # Collect values from comparable position players for this metric
            all_values = []
            for other_player_stats in filtered_stats_list:
                if isinstance(other_player_stats, dict) and metric_key in other_player_stats:
                    val = other_player_stats[metric_key]
                    if isinstance(val, (int, float)):
                        all_values.append(val)

            if not all_values:
                continue

            # Sort descending and calculate percentile rank
            sorted_values = sorted(all_values, reverse=True)
            try:
                rank = sorted_values.index(player_value) + 1
            except ValueError:
                rank = len(sorted_values)

            # Calculate percentile: (players_behind / total_players-1) * 100
            total_players = len(sorted_values)
            percentile = ((total_players - rank) / max(1, total_players - 1)) * 100 if total_players > 1 else 100

            # Calculate z-score
            mean = sum(all_values) / len(all_values)
            variance = sum((x - mean) ** 2 for x in all_values) / len(all_values)
            std_dev = variance ** 0.5
            z_score = (player_value - mean) / std_dev if std_dev > 0 else 0.0

            # Create Metric object
            metric = Metric(
                value=player_value,
                value_pg=player_value,  # Assuming value_pg is the same as value for player metrics
                percentile=percentile,
                percentile_order=rank,
                percentile_total=total_players,
                sample_size=sample_size,
                average=mean,
                z_score=z_score,
                label="",
                label2="",
                bar_label_low="",
                bar_label_high=""
            )

            result[metric_key] = metric

        print(f"[DataProvider] ✓ Processed {len(result)} metrics for {player_name}")
        return result

    def process_team_stats(self, stats) -> Dict:
        """
        Process team statistics and calculate percentiles and z-scores for all teams.

        Args:
            stats: List or dict from allseason_stats.json file

        Returns:
            Dictionary organized by team_name with metrics for each team:
            {
                'Team A': {'team_season_xg': Metric(...), ...},
                'Team B': {'team_season_xg': Metric(...), ...},
                ...
            }
        """
        from .metrics import Metric

        # Handle both list and dict structures
        if isinstance(stats, list):
            stats_list = stats
        else:
            stats_list = list(stats.values()) if isinstance(stats, dict) else []

        print(f"[DataProvider] Processing stats for all teams ({len(stats_list)} teams)")
        all_teams_result = {}

        for team_data in stats_list:
            if not isinstance(team_data, dict):
                continue

            current_team_name = team_data.get('team_name', 'Unknown')
            sample_size = team_data.get('team_season_matches', 0)

            # Extract all team_season_* metrics for this team
            team_metrics = {}
            for key, value in team_data.items():
                if key.startswith('team_season_') and key != 'team_season_matches' and isinstance(value, (int, float)):
                    team_metrics[key] = value

            # Calculate percentiles and z-scores for each metric
            team_result = {}

            for metric_key, team_value in team_metrics.items():
                # Collect values from all teams for this metric
                all_values = []
                for other_team_stats in stats_list:
                    if isinstance(other_team_stats, dict) and metric_key in other_team_stats:
                        val = other_team_stats[metric_key]
                        if isinstance(val, (int, float)):
                            all_values.append(val)

                if not all_values:
                    continue

                # Sort descending and calculate percentile rank
                sorted_values = sorted(all_values, reverse=True)
                try:
                    rank = sorted_values.index(team_value) + 1
                except ValueError:
                    rank = len(sorted_values)

                # Calculate percentile: (teams_behind / total_teams-1) * 100
                total_teams = len(sorted_values)
                percentile = ((total_teams - rank) / max(1, total_teams - 1)) * 100 if total_teams > 1 else 100

                # Calculate z-score
                mean = sum(all_values) / len(all_values)
                variance = sum((x - mean) ** 2 for x in all_values) / len(all_values)
                std_dev = variance ** 0.5
                z_score = (team_value - mean) / std_dev if std_dev > 0 else 0.0

                # Create Metric object
                metric = Metric(
                    value=team_value,
                    value_pg=team_value,
                    percentile=percentile,
                    percentile_order=rank,
                    percentile_total=total_teams,
                    sample_size=sample_size,
                    average=mean,
                    z_score=z_score,
                    label="",
                    label2="",
                    bar_label_low="",
                    bar_label_high=""
                )

                team_result[metric_key] = metric

            all_teams_result[current_team_name] = team_result

        print(f"[DataProvider] ✓ Processed metrics for all {len(all_teams_result)} teams")
        return all_teams_result

    def process_team_stats_sk(self, stats) -> Dict:
        """
        Process SkillCorner team physical statistics and calculate percentiles and z-scores for all teams.

        Args:
            stats: List or dict from a SkillCorner teams_physical_*.json file

        Returns:
            Dictionary organized by team_name with metrics for each team:
            {
                'Team A': {'metric_key': Metric(...), ...},
                'Team B': {'metric_key': Metric(...), ...},
                ...
            }
        """
        from .metrics import Metric

        # Handle both list and dict structures
        if isinstance(stats, list):
            stats_list = stats
        else:
            stats_list = list(stats.values()) if isinstance(stats, dict) else []

        print(f"[DataProvider] Processing SkillCorner stats for all teams ({len(stats_list)} teams)")
        all_teams_result = {}

        for team_data in stats_list:
            if not isinstance(team_data, dict):
                continue

            current_team_name = team_data.get('team_name', 'Unknown')

            # Extract all metrics for this team (skip identifying fields)
            team_metrics = {}
            for key, value in team_data.items():
                if key not in ('team_name', 'team_id') and isinstance(value, (int, float)):
                    team_metrics[key] = value

            # Calculate percentiles and z-scores for each metric
            team_result = {}

            for metric_key, team_value in team_metrics.items():
                # Collect values from all teams for this metric
                all_values = []
                for other_team_stats in stats_list:
                    if isinstance(other_team_stats, dict) and metric_key in other_team_stats:
                        val = other_team_stats[metric_key]
                        if isinstance(val, (int, float)):
                            all_values.append(val)

                if not all_values:
                    continue

                # Sort descending and calculate percentile rank
                sorted_values = sorted(all_values, reverse=True)
                try:
                    rank = sorted_values.index(team_value) + 1
                except ValueError:
                    rank = len(sorted_values)

                # Calculate percentile: (teams_behind / total_teams-1) * 100
                total_teams = len(sorted_values)
                percentile = ((total_teams - rank) / max(1, total_teams - 1)) * 100 if total_teams > 1 else 100

                # Calculate z-score
                mean = sum(all_values) / len(all_values)
                variance = sum((x - mean) ** 2 for x in all_values) / len(all_values)
                std_dev = variance ** 0.5
                z_score = (team_value - mean) / std_dev if std_dev > 0 else 0.0

                # Create Metric object
                metric = Metric(
                    value=team_value,
                    value_pg=team_value,
                    percentile=percentile,
                    percentile_order=rank,
                    percentile_total=total_teams,
                    sample_size=1,
                    average=mean,
                    z_score=z_score,
                    label="",
                    label2="",
                    bar_label_low="",
                    bar_label_high=""
                )

                team_result[metric_key] = metric

            all_teams_result[current_team_name] = team_result

        print(f"[DataProvider] ✓ Processed SkillCorner metrics for all {len(all_teams_result)} teams")
        return all_teams_result

    def _load_name_overrides(self) -> Dict[str, str]:
        """
        Load manual StatsBomb<->SkillCorner player name overrides, for players whose
        names don't match automatically (exact match or token-subset fallback) in
        process_player_stats_sk().

        Reads data_temp/skillcorner_name_overrides.json once per DataProvider instance
        and caches the result; subsequent calls reuse the cached dict.

        Returns:
            Dict mapping StatsBomb player_name -> SkillCorner player_name
        """
        if self._name_overrides is not None:
            return self._name_overrides

        overrides_file = self.data_root.parent / 'skillcorner_name_overrides.json'
        overrides = {}

        if overrides_file.exists():
            try:
                with open(overrides_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for pair in data.get('overrides', []):
                    sk_name = pair.get('skillcorner_name')
                    sb_name = pair.get('statsbomb_name')
                    if sk_name and sb_name:
                        overrides[sb_name] = sk_name
                print(f"[DataProvider] ✓ Loaded {len(overrides)} name override(s) from {overrides_file}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DataProvider] Error loading name overrides file {overrides_file}: {e}")
        else:
            print(f"[DataProvider] No name overrides file found at {overrides_file}")

        self._name_overrides = overrides
        return overrides

    def process_player_stats_sk(self, stats, competition_id: int, season_id: int, player_id: int) -> Dict:
        """
        Process SkillCorner player physical statistics and calculate percentiles and z-scores.
        Only compares against players in similar positions using POSITION_COMPARISON_SETS -
        exactly the same logic as process_player_stats() - with position looked up from the
        matching StatsBomb player_stats.json file, since SkillCorner data has no position field.

        StatsBomb and SkillCorner player IDs are different, unrelated ID spaces, so players are
        matched across the two datasets by name: first an exact match, then - for cases like
        "Stephen Duke-McKenna" (SkillCorner) vs "Stephen Winston Duke-McKenna" (StatsBomb) - a
        fallback match on normalized name-token subsets.

        Args:
            stats: List or dict from a SkillCorner player_physical_*.json file
            competition_id: StatsBomb competition ID (to load the matching player_stats.json)
            season_id: StatsBomb season ID (to load the matching player_stats.json)
            player_id: StatsBomb ID of the player to process

        Returns:
            Dictionary with Metric objects for the given player, keyed by SkillCorner metric names
        """
        from .metrics import Metric

        # Handle both list and dict structures
        if isinstance(stats, list):
            sk_stats_list = stats
        else:
            sk_stats_list = list(stats.values()) if isinstance(stats, dict) else []

        # Load StatsBomb player_stats.json - this is where primary_position and full names live
        sb_filename = f"competition_{competition_id}_season_{season_id}_player_stats.json"
        sb_stats_file = self.data_root.parent / sb_filename

        print(f"[DataProvider] Looking for StatsBomb player stats file: {sb_stats_file}")

        if not sb_stats_file.exists():
            print(f"[DataProvider] StatsBomb player stats file not found: {sb_stats_file}")
            return {}

        try:
            with open(sb_stats_file, 'r', encoding='utf-8') as f:
                sb_stats = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[DataProvider] Error loading StatsBomb player stats file {sb_stats_file}: {e}")
            return {}

        sb_stats_list = sb_stats if isinstance(sb_stats, list) else (
            list(sb_stats.values()) if isinstance(sb_stats, dict) else []
        )

        # Find the target player's StatsBomb record by player_id
        sb_player_data = None
        for p in sb_stats_list:
            if isinstance(p, dict) and p.get('player_id') == player_id:
                sb_player_data = p
                break

        if not sb_player_data:
            print(f"[DataProvider] Player ID '{player_id}' not found in StatsBomb stats")
            return {}

        player_name = sb_player_data.get('player_name', f'Player {player_id}')
        player_position_text = sb_player_data.get('primary_position')

        # Get player position from primary_position field and find corresponding ID
        player_position_id = None
        for pos_id, pos_name in self.PLAYER_POSITIONS.items():
            if pos_name == player_position_text:
                player_position_id = pos_id
                break

        if player_position_id is None:
            print(f"[DataProvider] Position '{player_position_text}' not found in PLAYER_POSITIONS")
            return {}

        comparison_positions = self.POSITION_COMPARISON_SETS.get(player_position_id, {player_position_id})

        # Convert position IDs back to position names for filtering
        comparable_position_names = {
            self.PLAYER_POSITIONS.get(pos_id) for pos_id in comparison_positions
        }

        # StatsBomb players in a comparable position - this is the name-matching pool
        comparable_sb_players = [
            p for p in sb_stats_list
            if isinstance(p, dict) and p.get('primary_position') in comparable_position_names
        ]

        name_overrides = self._load_name_overrides()

        def normalize_name(name: str) -> set:
            """Lowercase, treat hyphens as spaces, and split into a token set."""
            return set(name.replace('-', ' ').lower().split())

        def find_sk_match(sb_name: str):
            # Names to try: the StatsBomb name itself, plus a manually-mapped
            # SkillCorner name if one is defined (for pairs the automatic matching
            # below can't resolve, e.g. "Pemi Aderoju" vs "Oluwalopemiwa Aderoju")
            candidate_names = [sb_name]
            override_name = name_overrides.get(sb_name)
            if override_name:
                candidate_names.append(override_name)

            # 1) Exact match
            for sk_player in sk_stats_list:
                if isinstance(sk_player, dict) and sk_player.get('player_name') in candidate_names:
                    return sk_player

            # 2) Fallback: normalized name-token subset match, e.g.
            #    "Priestley Farquharson" vs "Priestley Tyler Heginbottom Farquharson"
            for candidate_name in candidate_names:
                candidate_tokens = normalize_name(candidate_name)
                if not candidate_tokens:
                    continue
                for sk_player in sk_stats_list:
                    if not isinstance(sk_player, dict):
                        continue
                    sk_tokens = normalize_name(sk_player.get('player_name', ''))
                    if sk_tokens and (candidate_tokens <= sk_tokens or sk_tokens <= candidate_tokens):
                        return sk_player
            return None

        # Match every comparable StatsBomb player to a SkillCorner entry (skip unmatched)
        filtered_sk_list = []
        target_sk_player = None
        for sb_player in comparable_sb_players:
            sb_name = sb_player.get('player_name', '')
            sk_player = find_sk_match(sb_name)
            if sk_player is None:
                continue
            filtered_sk_list.append(sk_player)
            if sb_player.get('player_id') == player_id:
                target_sk_player = sk_player

        if target_sk_player is None:
            print(f"[DataProvider] Could not match SkillCorner data for {player_name} (ID: {player_id})")
            return {}

        sample_size = len(filtered_sk_list)
        print(f"[DataProvider] Processing SkillCorner stats for {player_name} (ID: {player_id}), position: {player_position_text}, sample_size: {sample_size}")

        # Extract all numeric metrics for this player (skip identifying fields)
        skip_fields = {'player_id', 'player_name', 'player_short_name', 'player_birthdate'}
        player_metrics = {
            key: value for key, value in target_sk_player.items()
            if key not in skip_fields and isinstance(value, (int, float))
        }

        result = {
            'player_id': player_id,
            'player_name': player_name,
            'player_position': player_position_text,
            'sample_size': sample_size,
        }

        for metric_key, player_value in player_metrics.items():
            # Collect values from comparable, matched players for this metric
            all_values = []
            for other_sk_player in filtered_sk_list:
                if isinstance(other_sk_player, dict) and metric_key in other_sk_player:
                    val = other_sk_player[metric_key]
                    if isinstance(val, (int, float)):
                        all_values.append(val)

            if not all_values:
                continue

            # Sort descending and calculate percentile rank
            sorted_values = sorted(all_values, reverse=True)
            try:
                rank = sorted_values.index(player_value) + 1
            except ValueError:
                rank = len(sorted_values)

            # Calculate percentile: (players_behind / total_players-1) * 100
            total_players = len(sorted_values)
            percentile = ((total_players - rank) / max(1, total_players - 1)) * 100 if total_players > 1 else 100

            # Calculate z-score
            mean = sum(all_values) / len(all_values)
            variance = sum((x - mean) ** 2 for x in all_values) / len(all_values)
            std_dev = variance ** 0.5
            z_score = (player_value - mean) / std_dev if std_dev > 0 else 0.0

            # Create Metric object
            metric = Metric(
                value=player_value,
                value_pg=player_value,
                percentile=percentile,
                percentile_order=rank,
                percentile_total=total_players,
                sample_size=sample_size,
                average=mean,
                z_score=z_score,
                label="",
                label2="",
                bar_label_low="",
                bar_label_high=""
            )

            result[metric_key] = metric

        print(f"[DataProvider] ✓ Processed {len(result)} SkillCorner metrics for {player_name}")
        return result

    def get_team_stats(self, competition_id: int, season_id: int, team_name: str = None, week_no: int = None) -> Dict:
        """
        Load aggregated season statistics for all teams in a competition and season.

        Args:
            competition_id: StatsBomb competition ID (e.g., 5)
            season_id: StatsBomb season ID (e.g., 351)
            team_name: Optional team name. Only takes effect when week_no is also
                    given: team_name's season-stats entry is replaced with its
                    match-level stats from that week (see
                    _apply_week_team_stats_override). Every other team's entry is
                    left untouched.
            week_no: Optional week number. See team_name.

        Returns:
            Dictionary organized by team_name with metrics for each team:
            {
                'Team A': {'team_season_xg': Metric(...), ...},
                'Team B': {'team_season_xg': Metric(...), ...},
                ...
            }

        Example:
            stats = provider.get_team_stats(5, 351)
            Returns: Dict from competition_5_season_351_allseason_stats.json with all teams
        """
        # Construct filename: competition_5_season_351_allseason_stats.json
        filename = f"competition_{competition_id}_season_{season_id}_allseason_stats.json"

        # Search in data_temp folder
        data_temp_root = self.data_root.parent
        stats_file = data_temp_root / filename

        print(f"[DataProvider] Looking for stats file: {stats_file}")

        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    print(f"[DataProvider] ✓ Loaded stats from {stats_file}")

                    if team_name is not None and week_no is not None:
                        stats = self._apply_week_team_stats_override(stats, team_name, week_no)

                    # Process all teams and return full stats
                    all_teams_stats = self.process_team_stats(stats)
                    return all_teams_stats
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DataProvider] Error loading stats file {stats_file}: {e}")
                return {}
        else:
            print(f"[DataProvider] Stats file not found: {stats_file}")
            return {}

    def _apply_week_team_stats_override(self, stats, team_name: str, week_no: int):
        """
        Replace team_name's entry in the season-stats list with its match-level
        stats from Week{week_no}_..._team_stats.json, so a report can be built
        from just that one week's numbers instead of the season average. Every
        other team's entry in `stats` is left untouched.

        The team_stats.json file holds one object per team in that match (this
        team and its opponent); only the object matching team_name is used.
        Its 'team_match_*' keys are renamed to 'team_season_*' so the result
        is picked up by process_team_stats() exactly like the season-stats
        file's own fields.

        Args:
            stats: List (or dict) loaded from the allseason_stats.json file
            team_name: Team whose entry should be overridden
            week_no: Week number to pull the override from

        Returns:
            The stats list with team_name's entry replaced (or unchanged if no
            matching week_stats file / team entry could be found).
        """
        team_dir = self.data_root / team_name
        week_stats_matches = sorted(team_dir.glob(f"*/Week{week_no}_*_team_stats.json"))

        if not week_stats_matches:
            print(f"[DataProvider] No team_stats.json found for {team_name}, week {week_no} under {team_dir}")
            return stats

        week_stats_file = week_stats_matches[0]
        print(f"[DataProvider] Overriding {team_name}'s season stats with week {week_no} stats from {week_stats_file}")

        try:
            with open(week_stats_file, 'r', encoding='utf-8') as f:
                week_stats = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[DataProvider] Error loading week stats file {week_stats_file}: {e}")
            return stats

        week_stats_list = week_stats if isinstance(week_stats, list) else (
            list(week_stats.values()) if isinstance(week_stats, dict) else []
        )

        team_week_entry = next(
            (entry for entry in week_stats_list if isinstance(entry, dict) and entry.get('team_name') == team_name),
            None
        )

        if team_week_entry is None:
            print(f"[DataProvider] {team_name} not found in {week_stats_file}")
            return stats

        stats_list = stats if isinstance(stats, list) else (list(stats.values()) if isinstance(stats, dict) else [])

        # team_name's existing season-stats entry, used below to match its '_pg'
        # naming convention for the renamed keys.
        original_entry = next(
            (entry for entry in stats_list if isinstance(entry, dict) and entry.get('team_name') == team_name),
            None
        )

        # Rename 'team_match_*' keys to 'team_season_*' so process_team_stats() picks them up.
        # If team_name's existing season-stats entry has a '_pg' (per game) suffixed
        # version of this field (e.g. 'team_season_np_xg_pg' instead of
        # 'team_season_np_xg'), use that suffixed name too, so the override lands on
        # the same field name the rest of the app expects.
        renamed_entry = {}
        for key, value in team_week_entry.items():
            if key.startswith('team_match'):
                key = 'team_season' + key[len('team_match'):]
            if original_entry is not None and f"{key}_pg" in original_entry:
                key = f"{key}_pg"
            renamed_entry[key] = value

        updated_stats = []
        replaced = False
        for entry in stats_list:
            if isinstance(entry, dict) and entry.get('team_name') == team_name:
                updated_stats.append(renamed_entry)
                replaced = True
            else:
                updated_stats.append(entry)

        if not replaced:
            print(f"[DataProvider] {team_name} not found in season stats list - appending week stats entry")
            updated_stats.append(renamed_entry)

        return updated_stats

    def _match_reference_name(self, name: str, candidate_names) -> str:
        """
        Match `name` against a set of reference names, handling minor naming
        differences between data sources - e.g. SkillCorner's 'Crawley Town FC'
        vs StatsBomb's 'Crawley Town'.

        Tries an exact match first, then falls back to a normalized
        token-subset match (hyphens treated as spaces, case-insensitive) -
        the same approach used to match player names in process_player_stats_sk().

        Returns the matching candidate name, or None if no match is found.
        """
        if name in candidate_names:
            return name

        def normalize(n: str) -> set:
            return set(n.replace('-', ' ').lower().split())

        name_tokens = normalize(name)
        if not name_tokens:
            return None

        for candidate in candidate_names:
            candidate_tokens = normalize(candidate)
            if candidate_tokens and (name_tokens <= candidate_tokens or candidate_tokens <= name_tokens):
                return candidate

        return None

    def _apply_match_team_stats_override_sk(self, sections: Dict, section_keys: Dict, skillcorner_root: Path,
                                             competition_id: int, season_id: int,
                                             team_name: str, home_name: str, away_name: str) -> Dict:
        """
        Replace team_name's season-level entry in each section of `sections` with its
        match-level stats for the home_name vs away_name match, read from the
        *_teams_match_physical.json file.
        """
        match_filename = f"competition_{competition_id}_season_{season_id}_teams_match_physical.json"
        match_stats_file = skillcorner_root / match_filename

        match_sections = {}
        if match_stats_file.exists():
            try:
                with open(match_stats_file, 'r', encoding='utf-8') as f:
                    match_sections = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DataProvider] Error loading SkillCorner match stats file {match_stats_file}: {e}")
        else:
            print(f"[DataProvider] SkillCorner match stats file not found: {match_stats_file}")

        for section_key in section_keys.values():
            section_stats = sections.get(section_key)
            match_section_stats = match_sections.get(section_key)
            if not section_stats or not match_section_stats:
                continue

            section_list = section_stats if isinstance(section_stats, list) else list(section_stats.values())
            match_list = match_section_stats if isinstance(match_section_stats, list) else list(match_section_stats.values())

            sk_team_names = {
                entry.get('team_name') for entry in section_list
                if isinstance(entry, dict) and entry.get('team_name')
            }

            team_name_sk = self._match_reference_name(team_name, sk_team_names)
            home_name_sk = self._match_reference_name(home_name, sk_team_names)
            away_name_sk = self._match_reference_name(away_name, sk_team_names)

            if team_name_sk is None or home_name_sk is None or away_name_sk is None:
                print(f"[DataProvider] Could not match team names for SkillCorner match override "
                      f"(team={team_name}, home={home_name}, away={away_name}, section={section_key})")
                continue

            match_name_sk = f"{home_name_sk} v {away_name_sk}"

            match_entry = next(
                (entry for entry in match_list
                 if isinstance(entry, dict) and entry.get('team_name') == team_name_sk
                 and entry.get('match_name') == match_name_sk),
                None
            )

            if match_entry is None:
                print(f"[DataProvider] No match-level SkillCorner stats found for "
                      f"'{team_name_sk}' in match '{match_name_sk}' (section={section_key})")
                continue

            sections[section_key] = [
                match_entry if isinstance(entry, dict) and entry.get('team_name') == team_name_sk else entry
                for entry in section_list
            ]

        return sections

    def get_team_stats_sk(self, competition_id: int, season_id: int, team_name: str = None,
                           home_name: str = None, away_name: str = None) -> Dict:
        """
        Load SkillCorner physical statistics for all teams in a competition and season.

        Args:
            competition_id: StatsBomb competition ID (e.g., 5)
            season_id: StatsBomb season ID (e.g., 351)
            team_name: Optional StatsBomb team name. When given together with
                home_name and away_name, team_name's season-level entry in each
                section is replaced with its match-level stats for that match
                (from the *_teams_match_physical.json file).
            home_name: Optional StatsBomb home team name for the match to pull
                team_name's override stats from.
            away_name: Optional StatsBomb away team name for the match to pull
                team_name's override stats from.

        Returns:
            Dictionary keyed by physical data type, each holding the processed
            result from process_team_stats_sk() for that section:
            {
                'physical_all': {...},
                'physical_otip': {...},
                'physical_tip': {...},
            }

        Example:
            stats = provider.get_team_stats_sk(5, 351)
            Returns: Dict built from the 'all'/'otip'/'tip' sections of
            competition_5_season_351_teams_physical.json
        """
        # Construct filename: competition_5_season_351_teams_physical.json
        filename = f"competition_{competition_id}_season_{season_id}_teams_physical.json"

        # Search in data_temp/skillcorner folder
        skillcorner_root = self.data_root.parent / 'skillcorner'
        stats_file = skillcorner_root / filename

        print(f"[DataProvider] Looking for SkillCorner stats file: {stats_file}")

        sections = {}
        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    sections = json.load(f)
                    print(f"[DataProvider] ✓ Loaded SkillCorner stats from {stats_file}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DataProvider] Error loading SkillCorner stats file {stats_file}: {e}")
        else:
            print(f"[DataProvider] SkillCorner stats file not found: {stats_file}")

        # Map each result key to its section within the merged file
        section_keys = {
            'physical_all': 'all',
            'physical_otip': 'otip',
            'physical_tip': 'tip',
        }

        if team_name and home_name and away_name:
            sections = self._apply_match_team_stats_override_sk(
                sections, section_keys, skillcorner_root, competition_id, season_id,
                team_name, home_name, away_name
            )

        results = {}
        for result_key, section_key in section_keys.items():
            section_stats = sections.get(section_key)
            results[result_key] = self.process_team_stats_sk(section_stats) if section_stats else {}

        # Remap SkillCorner team names onto StatsBomb team names (e.g. "Crawley Town FC" -> "Crawley Town")
        # so callers can look up results by the StatsBomb team_name used everywhere else in the report.
        statsbomb_team_names = set(self.get_team_stats(competition_id, season_id).keys())
        if statsbomb_team_names:
            for key in results:
                remapped = {}
                for sk_team_name, team_metrics in results[key].items():
                    matched_name = self._match_reference_name(sk_team_name, statsbomb_team_names)
                    if matched_name is None:
                        print(f"[DataProvider] Could not match SkillCorner team '{sk_team_name}' to a StatsBomb team name")
                    remapped[matched_name or sk_team_name] = team_metrics
                results[key] = remapped

        return results

    def get_player_stats_sk(self, competition_id: int, season_id: int, player_id: int, team_name: str = None,
                             home_name: str = None, away_name: str = None) -> Dict:
        """
        Load SkillCorner physical statistics for all players in a competition and season.

        Args:
            competition_id: StatsBomb competition ID (e.g., 5)
            season_id: StatsBomb season ID (e.g., 351)
            player_id: StatsBomb player ID
            team_name: Optional StatsBomb team name for player_id. When given
                together with home_name and away_name, player_id's season-level
                entry in each section is replaced with their match-level stats
                for that match (from the *_player_match_physical.json file).
            home_name: Optional StatsBomb home team name for the match to pull
                player_id's override stats from.
            away_name: Optional StatsBomb away team name for the match to pull
                player_id's override stats from.

        Returns:
            Dictionary keyed by physical data type, each holding the processed
            result from process_player_stats_sk() for that section:
            {
                'physical_all': {...},
                'physical_otip': {...},
                'physical_tip': {...},
                'physical_h1': {...},
                'physical_h2': {...},
            }

        Example:
            stats = provider.get_player_stats_sk(5, 351)
            Returns: Dict built from the 'tip'/'otip'/'h1'/'h2'/'all' sections of
            competition_5_season_351_player_physical.json
        """
        # Construct filename: competition_5_season_351_player_physical.json
        filename = f"competition_{competition_id}_season_{season_id}_player_physical.json"

        # Search in data_temp/skillcorner folder
        skillcorner_root = self.data_root.parent / 'skillcorner'
        stats_file = skillcorner_root / filename

        print(f"[DataProvider] Looking for SkillCorner stats file: {stats_file}")

        sections = {}
        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    sections = json.load(f)
                    print(f"[DataProvider] ✓ Loaded SkillCorner stats from {stats_file}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DataProvider] Error loading SkillCorner stats file {stats_file}: {e}")
        else:
            print(f"[DataProvider] SkillCorner stats file not found: {stats_file}")

        # Map each result key to its section within the merged file
        section_keys = {
            'player_tip': 'tip',
            'player_otip': 'otip',
            'player_h1': 'h1',
            'player_h2': 'h2',
            'player_all': 'all',
        }

        if team_name and home_name and away_name:
            sections = self._apply_match_player_stats_override_sk(
                sections, section_keys, skillcorner_root, competition_id, season_id,
                player_id, team_name, home_name, away_name
            )

        results = {}
        for result_key, section_key in section_keys.items():
            section_stats = sections.get(section_key)
            results[result_key] = self.process_player_stats_sk(section_stats, competition_id, season_id, player_id) if section_stats else {}

        return results

    def _get_statsbomb_player_name(self, competition_id: int, season_id: int, player_id: int) -> str:
        """Look up a StatsBomb player's name by player_id from competition_{id}_season_{id}_player_stats.json."""
        filename = f"competition_{competition_id}_season_{season_id}_player_stats.json"
        stats_file = self.data_root.parent / filename

        if not stats_file.exists():
            return None

        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

        stats_list = data if isinstance(data, list) else (list(data.values()) if isinstance(data, dict) else [])
        for entry in stats_list:
            if isinstance(entry, dict) and entry.get('player_id') == player_id:
                return entry.get('player_name')
        return None

    def _find_sk_player_name(self, sb_name: str, candidate_names) -> str:
        """
        Match a StatsBomb player name to a SkillCorner player name among `candidate_names`,
        honoring the manual name-override file first - same approach as
        process_player_stats_sk()'s find_sk_match().
        """
        name_overrides = self._load_name_overrides()
        override_name = name_overrides.get(sb_name)
        candidates_to_try = [sb_name] + ([override_name] if override_name else [])

        for candidate in candidates_to_try:
            matched = self._match_reference_name(candidate, candidate_names)
            if matched:
                return matched
        return None

    def _apply_match_player_stats_override_sk(self, sections: Dict, section_keys: Dict, skillcorner_root: Path,
                                                competition_id: int, season_id: int, player_id: int,
                                                team_name: str, home_name: str, away_name: str) -> Dict:
        """
        Replace player_id's season-level entry in each section of `sections` with its
        match-level stats for the home_name vs away_name match, read from the
        *_player_match_physical.json file.

        Some season-level metric names end in '_top5' or '_top3' (e.g. 'psv99_top5',
        'peak_velocity_top3'); the match-level data holds the same metric without that
        suffix (e.g. 'psv99', 'peak_velocity'). The suffix is restored on the
        overridden entry's keys so downstream code keeps using the original,
        season-style metric names.
        """
        match_filename = f"competition_{competition_id}_season_{season_id}_player_match_physical.json"
        match_stats_file = skillcorner_root / match_filename

        match_sections = {}
        if match_stats_file.exists():
            try:
                with open(match_stats_file, 'r', encoding='utf-8') as f:
                    match_sections = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DataProvider] Error loading SkillCorner player match stats file {match_stats_file}: {e}")
        else:
            print(f"[DataProvider] SkillCorner player match stats file not found: {match_stats_file}")

        sb_player_name = self._get_statsbomb_player_name(competition_id, season_id, player_id)
        if sb_player_name is None:
            print(f"[DataProvider] Could not find StatsBomb player name for player_id {player_id}")
            return sections

        skip_fields = {'player_id', 'player_name', 'player_short_name', 'player_birthdate'}

        for section_key in section_keys.values():
            section_stats = sections.get(section_key)
            match_section_stats = match_sections.get(section_key)
            if not section_stats or not match_section_stats:
                continue

            section_list = section_stats if isinstance(section_stats, list) else list(section_stats.values())
            match_list = match_section_stats if isinstance(match_section_stats, list) else list(match_section_stats.values())

            sk_player_names = {
                entry.get('player_name') for entry in section_list
                if isinstance(entry, dict) and entry.get('player_name')
            }
            player_name_sk = self._find_sk_player_name(sb_player_name, sk_player_names)
            if player_name_sk is None:
                print(f"[DataProvider] Could not match SkillCorner player for '{sb_player_name}' (section={section_key})")
                continue

            original_entry = next(
                (entry for entry in section_list
                 if isinstance(entry, dict) and entry.get('player_name') == player_name_sk),
                None
            )
            if original_entry is None:
                continue

            sk_team_names = {
                entry.get('team_name') for entry in match_list
                if isinstance(entry, dict) and entry.get('team_name')
            }
            team_name_sk = self._match_reference_name(team_name, sk_team_names)
            home_name_sk = self._match_reference_name(home_name, sk_team_names)
            away_name_sk = self._match_reference_name(away_name, sk_team_names)

            if team_name_sk is None or home_name_sk is None or away_name_sk is None:
                print(f"[DataProvider] Could not match team names for SkillCorner player match override "
                      f"(team={team_name}, home={home_name}, away={away_name}, section={section_key})")
                continue

            match_name_sk = f"{home_name_sk} v {away_name_sk}"

            match_entry = next(
                (entry for entry in match_list
                 if isinstance(entry, dict) and entry.get('player_name') == player_name_sk
                 and entry.get('team_name') == team_name_sk
                 and entry.get('match_name') == match_name_sk),
                None
            )

            if match_entry is None:
                print(f"[DataProvider] No match-level SkillCorner stats found for "
                      f"'{player_name_sk}' in match '{match_name_sk}' (section={section_key})")
                continue

            renamed_entry = {}
            for key, value in original_entry.items():
                if key in skip_fields:
                    renamed_entry[key] = value
                    continue
                base_key = key[:-len('_top5')] if key.endswith('_top5') or key.endswith('_top3') else key
                renamed_entry[key] = match_entry.get(base_key, 0)

            sections[section_key] = [
                renamed_entry if isinstance(entry, dict) and entry.get('player_name') == player_name_sk else entry
                for entry in section_list
            ]

        return sections

    def get_player_stats(self, competition_id: int, season_id: int, player_id: int,
                          team_name: str = None, week_no: int = None) -> Dict:
        """
        Load aggregated player statistics for a competition and season.

        Args:
            competition_id: StatsBomb competition ID (e.g., 5)
            season_id: StatsBomb season ID (e.g., 351)
            player_id: StatsBomb player ID (e.g., 12345)
            team_name: Optional team name. Only takes effect when week_no is also
                    given: player_id's season metrics are overridden with their
                    match-level stats for that week (see
                    _load_week_player_match_stats / process_player_stats).
            week_no: Optional week number. See team_name.

        Returns:
            Dictionary with aggregated player stats, or empty dict if not found.

        Example:
            player_stats = provider.get_player_stats(5, 351)
            Returns: Dict from competition_5_season_351_player_stats.json
        """
        # Construct filename: competition_5_season_351_player_stats.json
        filename = f"competition_{competition_id}_season_{season_id}_player_stats.json"

        # Search in data_temp folder
        data_temp_root = self.data_root.parent
        player_stats_file = data_temp_root / filename

        print(f"[DataProvider] Looking for player stats file: {player_stats_file}")

        if player_stats_file.exists():
            try:
                with open(player_stats_file, 'r', encoding='utf-8') as f:
                    player_stats = json.load(f)
                    print(f"[DataProvider] ✓ Loaded player stats from {player_stats_file}")

                    match_stats = None
                    if team_name is not None and week_no is not None:
                        match_stats = self._load_week_player_match_stats(team_name, week_no, player_id)

                    return self.process_player_stats(player_stats, player_id, match_stats=match_stats)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DataProvider] Error loading player stats file {player_stats_file}: {e}")
                return {}
        else:
            print(f"[DataProvider] Player stats file not found: {player_stats_file}")
            return {}

    def _load_week_player_match_stats(self, team_name: str, week_no: int, player_id: int) -> Dict:
        """
        Load player_id's match-level stats dict from Week{week_no}_..._player_stats.json
        under team_name's season folder (e.g. Week10_Crawley Town_vs_Chesterfield_player_stats.json).

        Returns the matching player's dict, or None if the file or player entry isn't found.
        """
        team_dir = self.data_root / team_name
        week_stats_matches = sorted(team_dir.glob(f"*/Week{week_no}_*_player_stats.json"))

        if not week_stats_matches:
            print(f"[DataProvider] No player_stats.json found for {team_name}, week {week_no} under {team_dir}")
            return None

        week_stats_file = week_stats_matches[0]
        print(f"[DataProvider] Loading week {week_no} player match stats from {week_stats_file}")

        try:
            with open(week_stats_file, 'r', encoding='utf-8') as f:
                week_stats = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[DataProvider] Error loading week player stats file {week_stats_file}: {e}")
            return None

        week_stats_list = week_stats if isinstance(week_stats, list) else (
            list(week_stats.values()) if isinstance(week_stats, dict) else []
        )

        return next(
            (entry for entry in week_stats_list if isinstance(entry, dict) and entry.get('player_id') == player_id),
            None
        )

    def get_team_players(self, competition_id: int, season_id: int, team_name: str) -> List[int]:
        """
        Get list of player IDs for a specific team in a competition and season.

        Args:
            competition_id: StatsBomb competition ID (e.g., 5)
            season_id: StatsBomb season ID (e.g., 351)
            team_name: Team name to filter players (e.g., "Manchester United")

        Returns:
            List of player IDs for the specified team, or empty list if not found.

        Example:
            player_ids = provider.get_team_players(5, 351, "Manchester United")
            Returns: [12345, 12346, 12347, ...]
        """
        # Construct filename: competition_5_season_351_player_stats.json
        filename = f"competition_{competition_id}_season_{season_id}_player_stats.json"

        # Search in data_temp folder
        data_temp_root = self.data_root.parent
        player_stats_file = data_temp_root / filename

        print(f"[DataProvider] Looking for players from '{team_name}' in {player_stats_file}")

        if player_stats_file.exists():
            try:
                with open(player_stats_file, 'r', encoding='utf-8') as f:
                    player_stats = json.load(f)

                    # Handle both list and dict structures
                    if isinstance(player_stats, list):
                        stats_list = player_stats
                    else:
                        stats_list = list(player_stats.values()) if isinstance(player_stats, dict) else []

                    # Filter players by team_name and extract player_id's, excluding goalkeepers
                    team_player_ids = [
                        p.get('player_id') for p in stats_list
                        if isinstance(p, dict) and p.get('team_name') == team_name and p.get('player_id')
                        and p.get('primary_position') != 'Goalkeeper'
                    ]

                    print(f"[DataProvider] ✓ Found {len(team_player_ids)} players for team '{team_name}' (goalkeepers excluded)")
                    return team_player_ids
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DataProvider] Error loading player stats file {player_stats_file}: {e}")
                return []
        else:
            print(f"[DataProvider] Player stats file not found: {player_stats_file}")
            return []

    def get_all_player_stats(self, competition_id: int, season_id: int) -> Dict:
        """
        Load aggregated player statistics for all players in a competition and season.

        Args:
            competition_id: StatsBomb competition ID (e.g., 5)
            season_id: StatsBomb season ID (e.g., 351)

        Returns:
            Dictionary mapping player_id to player stats dict containing player_season_minutes and other metrics.
        """
        filename = f"competition_{competition_id}_season_{season_id}_player_stats.json"
        data_temp_root = self.data_root.parent
        player_stats_file = data_temp_root / filename

        print(f"[DataProvider] Loading all player stats from: {player_stats_file}")

        if player_stats_file.exists():
            try:
                with open(player_stats_file, 'r', encoding='utf-8') as f:
                    player_stats = json.load(f)
                    print(f"[DataProvider] ✓ Loaded stats for {len(player_stats)} players")

                    # Convert to dict keyed by player_id for easier lookup
                    result = {}
                    if isinstance(player_stats, list):
                        for player_data in player_stats:
                            if isinstance(player_data, dict) and 'player_id' in player_data:
                                result[player_data['player_id']] = player_data
                    elif isinstance(player_stats, dict):
                        for player_id, player_data in player_stats.items():
                            if isinstance(player_data, dict):
                                result[int(player_id) if player_id.isdigit() else player_id] = player_data

                    return result
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DataProvider] Error loading player stats file: {e}")
                return {}
        else:
            print(f"[DataProvider] Player stats file not found: {player_stats_file}")
            return {}

    def get_table(self, competition_id: int, season_id: int) -> Dict:
        """
        Build and return a league table from match data.

        Args:
            competition_id: StatsBomb competition ID (e.g., 5)
            season_id: StatsBomb season ID (e.g., 351)

        Returns:
            Dictionary organized by team_name with table stats:
            {
                'Team A': {
                    'rank': 1,
                    'team_name': 'Team A',
                    'played': 10,
                    'wins': 7,
                    'draws': 2,
                    'losses': 1,
                    'goals_for': 25,
                    'goals_against': 8,
                    'goal_difference': 17,
                    'points': 23
                },
                ...
            }
        """
        # Construct filename: competition_5_season_351_matches.json
        filename = f"competition_{competition_id}_season_{season_id}_matches.json"
        data_temp_root = self.data_root.parent
        matches_file = data_temp_root / filename

        print(f"[DataProvider] Loading league table from: {matches_file}")

        if not matches_file.exists():
            print(f"[DataProvider] Matches file not found: {matches_file}")
            return {}

        try:
            with open(matches_file, 'r', encoding='utf-8') as f:
                matches = json.load(f)
                print(f"[DataProvider] Loaded {len(matches)} matches")

            # Initialize team stats dictionary
            team_stats = {}

            # Process each match
            for match in matches:
                if not isinstance(match, dict):
                    continue

                # Only process matches with "available" status (matches that have been played)
                match_status = match.get('match_status')
                if match_status != 'available':
                    continue

                home_team = match.get('home_team', {})
                away_team = match.get('away_team', {})
                home_team_name = home_team if isinstance(home_team, str) else home_team.get('name', '')
                away_team_name = away_team if isinstance(away_team, str) else away_team.get('name', '')

                home_score = match.get('home_score')
                away_score = match.get('away_score')

                # Skip matches without scores (future/incomplete matches)
                if home_score is None or away_score is None:
                    continue

                # Initialize team if not in dict
                for team_name in [home_team_name, away_team_name]:
                    if team_name and team_name not in team_stats:
                        team_stats[team_name] = {
                            'team_name': team_name,
                            'played': 0,
                            'wins': 0,
                            'draws': 0,
                            'losses': 0,
                            'goals_for': 0,
                            'goals_against': 0,
                            'points': 0
                        }

                # Update home team stats
                if home_team_name:
                    team_stats[home_team_name]['played'] += 1
                    team_stats[home_team_name]['goals_for'] += home_score
                    team_stats[home_team_name]['goals_against'] += away_score

                    if home_score > away_score:
                        team_stats[home_team_name]['wins'] += 1
                        team_stats[home_team_name]['points'] += 3
                    elif home_score == away_score:
                        team_stats[home_team_name]['draws'] += 1
                        team_stats[home_team_name]['points'] += 1
                    else:
                        team_stats[home_team_name]['losses'] += 1

                # Update away team stats
                if away_team_name:
                    team_stats[away_team_name]['played'] += 1
                    team_stats[away_team_name]['goals_for'] += away_score
                    team_stats[away_team_name]['goals_against'] += home_score

                    if away_score > home_score:
                        team_stats[away_team_name]['wins'] += 1
                        team_stats[away_team_name]['points'] += 3
                    elif away_score == home_score:
                        team_stats[away_team_name]['draws'] += 1
                        team_stats[away_team_name]['points'] += 1
                    else:
                        team_stats[away_team_name]['losses'] += 1

            # Calculate goal difference and sort by points
            for team_name, stats in team_stats.items():
                stats['goal_difference'] = stats['goals_for'] - stats['goals_against']

            # Sort by points (desc), then goal difference (desc), then goals for (desc)
            sorted_teams = sorted(
                team_stats.items(),
                key=lambda x: (
                    -x[1]['points'],
                    -x[1]['goal_difference'],
                    -x[1]['goals_for']
                )
            )

            # Add ranking
            final_table = {}
            for rank, (team_name, stats) in enumerate(sorted_teams, 1):
                stats['rank'] = rank
                final_table[team_name] = stats

            print(f"[DataProvider] ✓ League table built with {len(final_table)} teams")
            return final_table

        except (json.JSONDecodeError, IOError) as e:
            print(f"[DataProvider] Error loading matches file: {e}")
            return {}
