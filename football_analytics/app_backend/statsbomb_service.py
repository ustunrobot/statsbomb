"""
StatsBomb API Integration Service

Handles all communication with StatsBomb API for:
- Fetching competitions (league + season combinations)
- Fetching teams in a competition
- Fetching players in a team
- Fetching match data
- Fetching event data

Uses statsbombpy library with authenticated credentials.
"""

import sys
from pathlib import Path
import statsbombpy.sb as sb
import pandas as pd
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# StatsBomb API Credentials (from data_loader.py)
DEFAULT_CREDENTIALS = {
    "user": "ustunrobot@gmail.com",
    "passwd": "waQMIar2",
}

class StatsBombService:
    """Service for fetching data from StatsBomb API"""

    def __init__(self, credentials: Optional[Dict[str, str]] = None):
        """
        Initialize StatsBomb service.

        Args:
            credentials: Dict with 'user' and 'passwd' keys. Uses default if not provided.
        """
        self.creds = credentials or DEFAULT_CREDENTIALS
        self.competitions_cache = None
        self.teams_cache = {}
        self.players_cache = {}

    def get_competitions(self, use_cache: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch all available competitions from StatsBomb API.

        Returns:
            List of competition dicts with keys:
                - id: competition_id
                - league: competition_name
                - season: season_name
                - season_id: season_id
                - year: year (extracted from season_name)
                - country: country_name
        """
        try:
            # Clear old caches to prevent stale data
            self.teams_cache.clear()
            self.players_cache.clear()

            # Return cached data if requested
            if use_cache and self.competitions_cache is not None:
                logger.info(f"Using cached competitions ({len(self.competitions_cache)} items)")
                return self.competitions_cache

            logger.info("Fetching competitions from StatsBomb API...")

            # Fetch competitions as DataFrame
            competitions_df = sb.competitions(fmt="dataframe", creds=self.creds)

            # Transform to list of dicts with our format
            competitions_list = []

            for _, row in competitions_df.iterrows():
                comp_id = int(row['competition_id'])
                season_id = int(row['season_id'])
                league = str(row['competition_name'])
                season = str(row['season_name'])
                country = str(row['country_name'])

                # Extract year from season name (e.g., "2024/25" -> 2024)
                try:
                    year = int(season.split('/')[0])
                except (ValueError, IndexError):
                    year = None

                competition = {
                    'id': comp_id,
                    'season_id': season_id,
                    'league': league,
                    'season': season,
                    'year': year,
                    'country': country,
                }

                competitions_list.append(competition)

            # Cache results
            self.competitions_cache = competitions_list

            logger.info(f"✓ Fetched {len(competitions_list)} competitions")

            return competitions_list

        except Exception as e:
            logger.error(f"Error fetching competitions: {e}")
            raise

    def get_teams(self, competition_id: int, season_id: int, use_cache: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch teams in a specific competition and season.

        Args:
            competition_id: StatsBomb competition ID
            season_id: StatsBomb season ID
            use_cache: Use cached data if available

        Returns:
            List of team dicts with keys:
                - id: team_id
                - name: team_name
        """
        try:
            cache_key = f"{competition_id}_{season_id}"

            # Return cached data if requested
            if use_cache and cache_key in self.teams_cache:
                logger.info(f"Using cached teams for competition {competition_id}, season {season_id}")
                return self.teams_cache[cache_key]

            logger.info(f"Fetching teams for competition {competition_id}, season {season_id}...")

            # Use API directly with raw request to avoid statsbombpy parsing issues
            import requests

            url = f"https://data.statsbombservices.com/api/v1/competitions/{competition_id}/seasons/{season_id}/matches"

            response = requests.get(
                url,
                auth=(self.creds['user'], self.creds['passwd']),
                timeout=30
            )

            if response.status_code != 200:
                logger.warning(f"API returned {response.status_code}, using fallback")
                # Fallback: return empty list
                teams_list = []
            else:
                matches_data = response.json()

                # Extract unique teams
                teams_dict = {}

                for match in matches_data:
                    # Home team
                    if 'home_team' in match:
                        home = match['home_team']
                        team_id = home.get('home_team_id')
                        team_name = home.get('home_team_name')
                        if team_id and team_name:
                            teams_dict[team_id] = team_name

                    # Away team
                    if 'away_team' in match:
                        away = match['away_team']
                        team_id = away.get('away_team_id')
                        team_name = away.get('away_team_name')
                        if team_id and team_name:
                            teams_dict[team_id] = team_name

                # Convert to list and sort
                teams_list = [
                    {'id': team_id, 'name': team_name}
                    for team_id, team_name in sorted(teams_dict.items(), key=lambda x: x[1])
                ]

            # Cache results
            self.teams_cache[cache_key] = teams_list

            logger.info(f"✓ Fetched {len(teams_list)} teams")

            return teams_list

        except Exception as e:
            logger.error(f"Error fetching teams: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Return empty list instead of raising
            return []

    def get_players(self, competition_id: int, season_id: int, team_id: int, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch players in a specific team for a competition/season.

        Args:
            competition_id: StatsBomb competition ID
            season_id: StatsBomb season ID
            team_id: StatsBomb team ID
            use_cache: Use cached data if available

        Returns:
            List of player dicts with keys:
                - id: player_id
                - name: player_name
                - number: shirt_number
        """
        try:
            cache_key = f"{competition_id}_{season_id}_{team_id}"

            # Return cached data if requested
            if use_cache and cache_key in self.players_cache:
                logger.info(f"Using cached players for team {team_id}")
                return self.players_cache[cache_key]

            logger.info(f"Fetching players for team {team_id} using season stats...")

            # Use player_season_stats to get all players who played for this team in the season
            stats_df = sb.player_season_stats(
                competition_id=competition_id,
                season_id=season_id,
                creds=self.creds,
                fmt="dataframe"
            )

            logger.info(f"Got {len(stats_df)} total player records")

            # Filter by team_id
            team_players = stats_df[stats_df['team_id'] == team_id]
            logger.info(f"Found {len(team_players)} players for team {team_id}")

            # Extract players for our team
            players_list = []
            for _, row in team_players.iterrows():
                players_list.append({
                    'id': int(row['player_id']),
                    'name': str(row['player_name']),
                    'number': None,  # Season stats don't include shirt number
                })

            # Sort by name
            players_list = sorted(players_list, key=lambda x: x['name'])

            # Cache results
            self.players_cache[cache_key] = players_list

            logger.info(f"✓ Fetched {len(players_list)} players for team {team_id}")

            return players_list

        except Exception as e:
            logger.error(f"Error fetching players: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Return empty list instead of raising
            return []

    def get_matches(self, competition_id: int, season_id: int) -> List[Dict[str, Any]]:
        """
        Fetch matches in a specific competition and season.

        Args:
            competition_id: StatsBomb competition ID
            season_id: StatsBomb season ID

        Returns:
            List of match dicts
        """
        try:
            logger.info(f"Fetching matches for competition {competition_id}, season {season_id}...")

            matches = sb.matches(
                competition_id=competition_id,
                season_id=season_id,
                creds=self.creds
            )

            matches_list = matches.to_dict('records')

            logger.info(f"✓ Fetched {len(matches_list)} matches")

            return matches_list

        except Exception as e:
            logger.error(f"Error fetching matches: {e}")
            raise

    def clear_cache(self):
        """Clear all cached data"""
        self.competitions_cache = None
        self.teams_cache = {}
        self.players_cache = {}
        logger.info("Cache cleared")


# Create global service instance
_service_instance = None

def get_service(credentials: Optional[Dict[str, str]] = None) -> StatsBombService:
    """
    Get or create the StatsBomb service instance.

    Args:
        credentials: Optional credentials dict

    Returns:
        StatsBombService instance
    """
    global _service_instance

    if _service_instance is None:
        _service_instance = StatsBombService(credentials=credentials)

    return _service_instance
