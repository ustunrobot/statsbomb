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
            data_root = module_dir / "data" / "teams"
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

                # Collect valid match files
                for event_file in season_folder.glob("Week*.json"):
                    # Skip 360frames files
                    if event_file.name.endswith("_360frames.json"):
                        continue

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
