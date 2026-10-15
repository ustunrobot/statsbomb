import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from skillcorner.client import SkillcornerClient

# Loads app_backend/.env explicitly (rather than relying on load_dotenv()'s
# default cwd-upward search), so this works both when imported by the Flask
# app and when run as a standalone CLI script from any directory.
load_dotenv(Path(__file__).parent.parent / 'app_backend' / '.env')

def fetch_skillcorner_physical_data(competition_id, competition_name, season_id, season_name):
    """Fetch and save SkillCorner team- and player-level physical data for one competition/season."""
    client = SkillcornerClient(
        username=os.getenv('SKILLCORNER_USERNAME'),
        password=os.getenv('SKILLCORNER_PASSWORD'),
    )

    sc_season_id = None
    seasons = client.get_seasons()
    for season in seasons:
        if season["name"] == season_name:
            sc_season_id = season["id"]
            print(season["id"])

    if sc_season_id is None:
        raise ValueError(f"No SkillCorner season found matching name '{season_name}'")

    sc_competition_id = None
    competitions = client.get_competitions(params={'season': sc_season_id})
    for competition in competitions:
        if competition["name"] == competition_name:
            sc_competition_id = competition["id"]
            print(sc_competition_id)

    if sc_competition_id is None:
        raise ValueError(f"No SkillCorner competition found matching name '{competition_name}' in season '{season_name}'")

    sc_competition_edition_id = None
    competition_editions = client.get_competition_competition_editions(competition_id=sc_competition_id)
    for competition_edition in competition_editions:
        if competition_edition["season"]["id"] == sc_season_id:
            sc_competition_edition_id = competition_edition["id"]
            print(sc_competition_edition_id)

    if sc_competition_edition_id is None:
        raise ValueError(f"No SkillCorner competition edition found for competition '{competition_name}', season '{season_name}'")

    common_params = {
        'season': sc_season_id,
        'competition': sc_competition_id,
        'competition_edition': sc_competition_edition_id,        
        'average_per': 'match',
        'data_version': '3.0.3',
    }
    common_params_p90 = {
            'season': sc_season_id,
            'competition': sc_competition_id,
            'competition_edition': sc_competition_edition_id,
            'average_per': 'p90',
            'data_version': '3.0.3',
    }

    data_temp_dir = Path(__file__).parent.parent / 'data_temp' / 'skillcorner'
    data_temp_dir.mkdir(parents=True, exist_ok=True)

    team_physical_data = {}
    player_physical_data = {}
    team_match_physical_data = {}
    player_match_physical_data = {}

    for possess in ["all", "tip", "otip"]:

        if possess == "all":
            team_data = client.get_physical(params={**common_params_p90, 'possession': possess, 'group_by': 'team'})
        else:
            team_data = client.get_physical(params={**common_params, 'possession': possess, 'group_by': 'team'})
        team_physical_data[possess] = team_data

        if possess == "all":
            player_data = client.get_physical(params={**common_params_p90, 'possession': possess, 'group_by': 'player'})
        else:
            player_data = client.get_physical(params={**common_params, 'possession': possess, 'group_by': 'player'})
        player_physical_data[possess] = player_data

        if possess == "all":
            player_physical_data['h1'] = client.get_physical(params={**common_params, 'period': 'h1', 'group_by': 'player'})
            player_physical_data['h2'] = client.get_physical(params={**common_params, 'period': 'h2', 'group_by': 'player'})

        if possess == "all":
            team_match_data = client.get_physical(params={**common_params_p90, 'possession': possess, 'group_by': 'team,match'})
        else:
            team_match_data = client.get_physical(params={**common_params, 'possession': possess, 'group_by': 'team,match'})
        team_match_physical_data[possess] = team_match_data

        if possess == "all":
            player_match_data = client.get_physical(params={**common_params_p90, 'possession': possess, 'group_by': 'player,match'})
        else:
            player_match_data = client.get_physical(params={**common_params, 'possession': possess, 'group_by': 'player,match'})
        player_match_physical_data[possess] = player_match_data

        if possess == "all":
            player_match_physical_data['h1'] = client.get_physical(params={**common_params, 'period': 'h1', 'group_by': 'player,match'})
            player_match_physical_data['h2'] = client.get_physical(params={**common_params, 'period': 'h2', 'group_by': 'player,match'})

    team_fname = f"competition_{competition_id}_season_{season_id}_teams_physical.json"
    with open(data_temp_dir / team_fname, 'w') as f:
        json.dump(team_physical_data, f, indent=2)

    player_fname = f"competition_{competition_id}_season_{season_id}_player_physical.json"
    with open(data_temp_dir / player_fname, 'w') as f:
        json.dump(player_physical_data, f, indent=2)

    team_match_fname = f"competition_{competition_id}_season_{season_id}_teams_match_physical.json"
    with open(data_temp_dir / team_match_fname, 'w') as f:
        json.dump(team_match_physical_data, f, indent=2)

    player_match_fname = f"competition_{competition_id}_season_{season_id}_player_match_physical.json"
    with open(data_temp_dir / player_match_fname, 'w') as f:
        json.dump(player_match_physical_data, f, indent=2)

    print(f"Saved to {data_temp_dir}")
    # return team_data, player_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch and save SkillCorner physical data for a competition/season')
    # the id fields are statsbom compatible
    #try to match the skillcorner ids from names
    #use the statsbomb file naming conventions
    parser.add_argument('competition_id', type=int, help='competition ID (e.g., 204)')
    parser.add_argument('competition_name', help='Competition name (e.g., "EFL League Two")')
    parser.add_argument('season_id', type=int, help='season ID (e.g., 131)')
    parser.add_argument('season_name', help='Season name (e.g., "2025/2026")')

    args = parser.parse_args()

    fetch_skillcorner_physical_data(
        competition_id=args.competition_id,
        competition_name=args.competition_name,
        season_id=args.season_id,
        season_name=args.season_name,
    )