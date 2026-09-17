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

    def get_matches(
        self,
        seasons: List[str] = None,
    ) -> List[Tuple[str, Dict]]:
        """
        Collect and load match event files in chronological order.

        Args:
            seasons: List of season folders to include (e.g. ['25-26', '26-27']).
                    Defaults to ['25-26', '26-27'].

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

    def _collect_match_files(self, seasons: List[str]) -> List[Path]:
        """
        Scan all team directories and collect valid match event files.

        Filters:
        - Must be JSON
        - Must start with 'Week'
        - Must not end with '_360frames.json'

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
                for event_file in season_folder.glob("Week1*.json"):
                    # Skip 360frames files
                    if event_file.name.endswith("_360frames.json"):
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
        def extract_week(path: Path) -> int:
            filename = path.name
            # Extract 'Week10' from 'Week10_Barnet_vs_Accrington Stanley.json'
            week_str = filename.split('_')[0].replace('Week', '')
            try:
                return int(week_str)
            except ValueError:
                return 999  # Put unparseable files at the end

        sorted_matches = sorted(seen_filenames.values(), key=extract_week)
        return sorted_matches

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

    def process_player_stats(self, stats, player_id: int) -> Dict:
        """
        Process player statistics and calculate percentiles and z-scores.
        Only compares against players in similar positions using POSITION_COMPARISON_SETS.

        Args:
            stats: List or dict from player_stats.json file
            player_id: ID of the player to process

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
            minutes_threshold = mean_minutes - std_dev if std_dev > 0 else 0
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

    def get_team_stats(self, competition_id: int, season_id: int) -> Dict:
        """
        Load aggregated season statistics for all teams in a competition and season.

        Args:
            competition_id: StatsBomb competition ID (e.g., 5)
            season_id: StatsBomb season ID (e.g., 351)

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
        data_temp_root = Path(__file__).parent.parent / "data_temp"
        stats_file = data_temp_root / filename

        print(f"[DataProvider] Looking for stats file: {stats_file}")

        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    print(f"[DataProvider] ✓ Loaded stats from {stats_file}")
                    # Process all teams and return full stats
                    all_teams_stats = self.process_team_stats(stats)
                    return all_teams_stats
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DataProvider] Error loading stats file {stats_file}: {e}")
                return {}
        else:
            print(f"[DataProvider] Stats file not found: {stats_file}")
            return {}

    def get_player_stats(self, competition_id: int, season_id: int, player_id: int) -> Dict:
        """
        Load aggregated player statistics for a competition and season.

        Args:
            competition_id: StatsBomb competition ID (e.g., 5)
            season_id: StatsBomb season ID (e.g., 351)
            player_id: StatsBomb player ID (e.g., 12345)

        Returns:
            Dictionary with aggregated player stats, or empty dict if not found.

        Example:
            player_stats = provider.get_player_stats(5, 351)
            Returns: Dict from competition_5_season_351_player_stats.json
        """
        # Construct filename: competition_5_season_351_player_stats.json
        filename = f"competition_{competition_id}_season_{season_id}_player_stats.json"

        # Search in data_temp folder
        data_temp_root = Path(__file__).parent.parent / "data_temp"
        player_stats_file = data_temp_root / filename

        print(f"[DataProvider] Looking for player stats file: {player_stats_file}")

        if player_stats_file.exists():
            try:
                with open(player_stats_file, 'r', encoding='utf-8') as f:
                    player_stats = json.load(f)
                    print(f"[DataProvider] ✓ Loaded player stats from {player_stats_file}")
                    return self.process_player_stats(player_stats, player_id)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DataProvider] Error loading player stats file {player_stats_file}: {e}")
                return {}
        else:
            print(f"[DataProvider] Player stats file not found: {player_stats_file}")
            return {}

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
        data_temp_root = Path(__file__).parent.parent / "data_temp"
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

                    # Filter players by team_name and extract player_id's
                    team_player_ids = [
                        p.get('player_id') for p in stats_list
                        if isinstance(p, dict) and p.get('team_name') == team_name and p.get('player_id')
                    ]

                    print(f"[DataProvider] ✓ Found {len(team_player_ids)} players for team '{team_name}'")
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
        data_temp_root = Path(__file__).parent.parent / "data_temp"
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
        data_temp_root = Path(__file__).parent.parent / "data_temp"
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
