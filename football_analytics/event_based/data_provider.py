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


class DataProvider:
    """Provides match event data for processing."""

    def __init__(self, data_root: str = None):
        if data_root is None:
            # Resolve data path relative to module location
            module_dir = Path(__file__).parent.parent
            data_root = module_dir / "data_temp" / "teams"
        self.data_root = Path(data_root)

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
            seasons = ['26-27']

        print(f"[DataProvider] Starting to collect match files for seasons: {seasons}")

        # Collect all valid match files across all teams
        match_files = self._collect_match_files(seasons)
        print(f"[DataProvider] Found {len(match_files)} total match files across all teams")

        # Deduplicate and sort by week
        unique_matches = self._deduplicate_and_sort(match_files)
        print(f"[DataProvider] After deduplication: {len(unique_matches)} unique matches")

        # Load and return event data
        matches = []
        for i, match_filename in enumerate(unique_matches, 1):
            event_data = self._load_event_file(match_filename)
            if event_data:
                matches.append((match_filename, event_data))
                print(f"[DataProvider] Loaded match {i}/{len(unique_matches)}: {match_filename.name}")
            else:
                print(f"[DataProvider] Failed to load match {i}/{len(unique_matches)}: {match_filename.name}")

        print(f"[DataProvider] Successfully loaded {len(matches)}/{len(unique_matches)} matches")
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

        # Use total number of players as sample_size
        sample_size = len(stats_list)
        player_name = player_data.get('player_name', f'Player {player_id}')
        print(f"[DataProvider] Processing stats for {player_name} (ID: {player_id}), sample_size: {sample_size}")

        # Extract all player_season_* metrics for this player
        player_metrics = {}
        for key, value in player_data.items():
            if key.startswith('player_season_') and isinstance(value, (int, float)):
                player_metrics[key] = value

        print(f"[DataProvider] Found {len(player_metrics)} metrics for {player_name}")

        # Calculate percentiles and z-scores for each metric
        result = {}

        for metric_key, player_value in player_metrics.items():
            # Collect values from all players for this metric
            all_values = []
            for other_player_stats in stats_list:
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

    def process_team_stats(self, stats, team_name: str) -> Dict:
        """
        Process team statistics and calculate percentiles and z-scores.

        Args:
            stats: List or dict from allseason_stats.json file
            team_name: Name of the team to process

        Returns:
            Dictionary with Metric objects for the given team, keyed by team_season_* metric names
        """
        from .metrics import Metric

        # Handle both list and dict structures
        if isinstance(stats, list):
            stats_list = stats
        else:
            stats_list = list(stats.values()) if isinstance(stats, dict) else []

        # Find the team data by team_name
        team_data = None
        for team_stats in stats_list:
            if isinstance(team_stats, dict) and team_stats.get('team_name') == team_name:
                team_data = team_stats
                break

        if not team_data:
            print(f"[DataProvider] Team '{team_name}' not found in stats")
            return {}

        # Get sample_size from team_season_matches
        sample_size = team_data.get('team_season_matches', 0)
        print(f"[DataProvider] Processing stats for {team_name}, sample_size: {sample_size}")

        # Extract all team_season_* metrics for this team
        team_metrics = {}
        for key, value in team_data.items():
            if key.startswith('team_season_') and key != 'team_season_matches' and isinstance(value, (int, float)):
                team_metrics[key] = value

        print(f"[DataProvider] Found {len(team_metrics)} metrics for {team_name}")

        # Calculate percentiles and z-scores for each metric
        result = {}

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

            result[metric_key] = metric

        print(f"[DataProvider] ✓ Processed {len(result)} metrics for {team_name}")
        return result

    def get_team_stats(self, competition_id: int, season_id: int, team_name: str) -> Dict:
        """
        Load aggregated season statistics for a competition and season.

        Args:
            competition_id: StatsBomb competition ID (e.g., 5)
            season_id: StatsBomb season ID (e.g., 351)
            team_name: Name of the team for which to load stats

        Returns:
            Dictionary with aggregated stats, or empty dict if not found.

        Example:
            stats = provider.get_team_stats(5, 351, "Arsenal")
            Returns: Dict from competition_5_season_351_allseason_stats.json
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
                    # Process for the specific team
                    processed_stats = self.process_team_stats(stats, team_name)
                    return processed_stats
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
