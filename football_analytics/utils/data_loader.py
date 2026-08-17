#!/usr/bin/env python3
"""Simple script to fetch competitions via the statsbombpy library.

Uses hardcoded StatsBomb credentials for authenticated API access.
"""

import argparse
import csv
import json
import sys
from pathlib import Path
sys.path.insert(0, "/home/baris/statsbomb")
#import statsbombpy as sb
import statsbombpy.sb as sb
import pandas as pd
import dataApp.pdf as pdf

def print_object(obj, indent=0, file=None):
    space = " " * indent

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                print(f"{space}{key}:", file=file)
                print_object(value, indent + 4, file)
            else:
                print(f"{space}{key}: {value}", file=file)

    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                print(f"{space}-")
                print_object(item, indent + 4, file)
            else:
                print(f"{space}- {item}", file=file)

    else:
        print(f"{space}{obj}", file=file)

def get_competitions(creds: dict | None = None, fmt: str = "dataframe"):
    """Return competitions data. If `creds` is provided, use authenticated API."""
    if creds is None:
        creds = {}
    return sb.competitions(fmt=fmt, creds=creds)

def fetch_events_with_360(match_id: int, creds: dict | None = None, include_360: bool = False):
    """Fetch events for a match, optionally including 360 frames."""
    if creds is None:
        creds = {}

    print(f"\nFetching events for match {match_id}...")
    events = sb.events(match_id, fmt="dict", creds=creds, include_360_metrics=True)
    print(f"✓ Fetched {len(events)} events")

    result = {"events": events, "frames": None}

    # Fetch 360 data if requested
    if include_360:
        print(f"Fetching 360 frames for match {match_id}...")
        try:
            frames = sb.api_client.frames(match_id, creds=creds)
            result["frames"] = frames
            print(f"✓ Fetched {len(frames)} 360 frames")
        except Exception as e:
            print(f"⚠ Could not fetch 360 frames: {e}")

    return result

def save_events_json(match_id: int, output_file: str, creds: dict | None = None):
    """Fetch events for a match and save as JSON file."""
    if creds is None:
        creds = {}

    # Fetch events and 360 data
    data = fetch_events_with_360(match_id, creds=creds, include_360=True)
    events = data["events"]
    frames = data["frames"]

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save events
    with open(output_path, 'w') as f:
        json.dump(events, f, indent=2)

    print(f"✓ Saved {len(events)} events to {output_file}")

    # Save 360 frames if available
    if frames:
        frames_file = output_path.stem + "_360frames.json"
        frames_path = output_path.parent / frames_file

        with open(frames_path, 'w') as f:
            json.dump(frames, f, indent=2)

        print(f"✓ Saved {len(frames)} 360 frames to {frames_path}")

def get_week_data(competition_id: int, season_id: int, week_no: int, creds: dict | None = None, data_dir: str = "teams", season_folder: str = "26-27"):
    """Fetch and save events for all matches of a specific team."""
    if creds is None:
        creds = {}

    matches = sb.matches(competition_id=competition_id, season_id=season_id, creds=creds)
    # Filter matches where team_name is home_team or away_team
    week_matches = matches[(matches['match_week'] == week_no)]

    print(f"\nFound {len(week_matches)} matches for week {week_no}")

    # Debug: Print available columns if needed
    # print(f"Available columns: {team_matches.columns.tolist()}")

    # Loop through matches and fetch events with 360 data
    for idx, match in week_matches.iterrows():
        match_id = match['match_id']
        home = match['home_team']
        away = match['away_team']        
        week = match['match_week']

        print(f"  [{idx + 1}] Week {week}: {home} vs {away} (Match ID: {match_id})")

        # Fetch events and 360 data
        data = fetch_events_with_360(match_id, creds=creds, include_360=True)
        events = data["events"]
        frames = data["frames"]

        for team in [home, away]:
            # Create team directory for home team
            team_dir = Path(data_dir) / team / season_folder
            team_dir.mkdir(parents=True, exist_ok=True)
            # Create filename
            filename = f"Week{week}_{home}_vs_{away}.json"
            filepath = team_dir / filename

            # Save events
            with open(filepath, 'w') as f:
                json.dump(events, f, indent=2)
            print(f"      ✓ Saved {len(events)} events to {filepath}")

            # Save 360 frames if available
            if frames:
                frames_filename = f"Week{week}_{home}_vs_{away}_360frames.json"
                frames_filepath = team_dir / frames_filename
                with open(frames_filepath, 'w') as f:
                    json.dump(frames, f, indent=2)
                print(f"      ✓ Saved {len(frames)} 360 frames to {frames_filepath}")

def get_team_data(competition_id: int, season_id: int, team_name: str, creds: dict | None = None, data_dir: str = "teams"):
    """Fetch and save events for all matches of a specific team."""
    if creds is None:
        creds = {}

    matches = sb.matches(competition_id=competition_id, season_id=season_id, creds=creds)

    # Filter matches where team_name is home_team or away_team
    team_matches = matches[(matches['home_team'] == team_name) | (matches['away_team'] == team_name)]

    print(f"\nFound {len(team_matches)} matches for {team_name}")

    # Create team directory
    team_dir = Path(data_dir) / team_name
    team_dir.mkdir(parents=True, exist_ok=True)

    # Debug: Print available columns if needed
    # print(f"Available columns: {team_matches.columns.tolist()}")

    # Loop through matches and fetch events with 360 data
    for idx, match in team_matches.iterrows():
        match_id = match['match_id']
        home = match['home_team']
        away = match['away_team']
        # Try different column names for week
        #week = match.get('week') or match.get('match_week') or match.get('week_number') or idx + 1
        week = match['match_week']

        print(f"  [{idx + 1}] Week {week}: {home} vs {away} (Match ID: {match_id})")

        # Fetch events and 360 data
        data = fetch_events_with_360(match_id, creds=creds, include_360=True)
        events = data["events"]
        frames = data["frames"]

        # Create filename
        filename = f"Week{week}_{home}_vs_{away}.json"
        filepath = team_dir / filename

        # Save events
        with open(filepath, 'w') as f:
            json.dump(events, f, indent=2)
        print(f"      ✓ Saved {len(events)} events to {filepath}")

        # Save 360 frames if available
        if frames:
            frames_filename = f"Week{week}_{home}_vs_{away}_360frames.json"
            frames_filepath = team_dir / frames_filename
            with open(frames_filepath, 'w') as f:
                json.dump(frames, f, indent=2)
            print(f"      ✓ Saved {len(frames)} 360 frames to {frames_filepath}")

def list_matches(competition_id: int, season_id: int, creds: dict | None = None):
    """Get and display available matches grouped by team."""
    if creds is None:
        creds = {}

    matches = sb.matches(competition_id=competition_id, season_id=season_id, creds=creds)
    pd.set_option('display.max_rows', None)
    print(matches[["match_id", "home_team", "away_team"]])


def list_competitions(creds: dict | None = None):
    """Get and display available competitions grouped by country."""
    if creds is None:
        creds = {}

    competitions_df = get_competitions(creds=creds, fmt="dataframe")

    print("\n" + "="*140)
    print("AVAILABLE STATSBOMB COMPETITIONS")
    print("="*140)

    # Group by country and competition
    for country in sorted(competitions_df['country_name'].unique()):
        country_comps = competitions_df[competitions_df['country_name'] == country]
        print(f"\n{country.upper()}")
        print("-" * 140)

        for comp_name in sorted(country_comps['competition_name'].unique()):
            comp_data = country_comps[country_comps['competition_name'] == comp_name]
            comp_id = comp_data.iloc[0]['competition_id']

            print(f"  Competition ID: {comp_id:4d} | {comp_name}")

            # Show seasons with season_id
            for _, row in comp_data.iterrows():
                season_name = row['season_name']
                season_id = row['season_id']
                print(f"                      ├─ Season ID: {season_id:4d} | {season_name}")

    print("\n" + "="*140)
    print(f"TOTAL: {len(competitions_df)} competition-season combinations")
    print("="*140 + "\n")

def main():
    p = argparse.ArgumentParser(description="Fetch competitions and events from StatsBomb API")
    p.add_argument("--list-competitions", action="store_true", help="List all available competitions")
    p.add_argument("--match-id", type=int, help="Match ID to fetch events for")
    p.add_argument("--save", help="Path to save file (JSON)")
    p.add_argument("--include-360", action="store_true", help="Also fetch and save 360 tracking data")
    p.add_argument("--list-matches", action="store_true", help="List all available matches is a comp and season")
    p.add_argument("--competition-id", type=int, help="Competition ID to fetch events for")
    p.add_argument("--season-id", type=int, help="Season ID to fetch events for")
    p.add_argument("--team-name", type=str, help="team to fetch events for all season")
    p.add_argument("--get-team-data", action="store_true", help="gets all match events of a team in a season")
    p.add_argument("--get-week-data", action="store_true", help="gets all match events in a week in a season")
    p.add_argument("--week-no", type=int, help="Week no to fetch events for")

    args = p.parse_args()

    creds = {
        "user": "ustunrobot@gmail.com",
        "passwd": "waQMIar2",
    }

    # List competitions if requested
    if args.list_competitions:
        list_competitions(creds=creds)
        return

    if args.list_matches:
        if args.competition_id and args.season_id:
            list_matches(args.competition_id, args.season_id, creds=creds)
        else:
            print("args needed --> competition and season ids")
        return

    if args.get_week_data:
            if args.week_no and args.competition_id and args.season_id:
                get_week_data(args.competition_id, args.season_id, args.week_no, creds=creds, data_dir="/home/baris/statsbomb/football_analytics/data/teams", season_folder="26-27" )
            else:
                print("args needed --> week no, competition and season ids")
            return
    
    if args.get_team_data:
        if args.team_name and args.competition_id and args.season_id:
            get_team_data(args.competition_id, args.season_id, args.team_name, creds=creds)
        else:
            print("args needed --> team-name competition and season ids")
        return

    # Fetch and save events for a specific match
    if args.match_id:
        if args.save:
            save_events_json(args.match_id, args.save, creds=creds)
        else:
            # Fetch without saving
            data = fetch_events_with_360(args.match_id, creds=creds)
            events = data["events"]
            frames = data["frames"]
            print(f"\nMatch {args.match_id}:")
            print(f"  Events: {len(events)}")
            if frames:
                print(f"  360 Frames: {len(frames)}")
        return

    # Default: fetch events for match 4002550
    events = sb.events(4002550, fmt="dict", creds=creds)

    #df = pd.json_normalize(events_dict)
    #selected = events.iloc[5:20]
    #selected.to_html("events_001.html", index=True)
    #print("Saved to events_rows_6_to_20.html")

    pdf.events_to_pdf(events, output_file="events_data_500_600.pdf", start_row=500, end_row=600)

    frames = sb.api_client.frames(4002550, creds=creds)

    #pdf.events_to_pdf(frames, output_file="frames_data_500_600.pdf", start_row=500, end_row=600, isList=True)

    print(len(frames))
    #print(events.keys())


    """competitions_df = get_competitions(creds=creds, fmt="dataframe")
    print(competitions_df[["competition_id", "competition_name", "season_id", "season_name"]].to_string(index=False))"""

    """events_dict = sb.events(4002550, split=False, fmt="dict", creds=creds)
    print(f"Total events returned for match 4002550: {len(events_dict)}")
    print("\nFirst 5 rows of the dict response:")
    for idx, (event_id, event_data) in enumerate(events_dict.items()):
        if idx >= 11:
            break
        if idx >= 5:
            print(event_id, event_data)
    events_df = sb.events(4002550, split=False, fmt="dataframe", creds=creds)
    print(f"Total events returned for match 4002550: {len(events_df)}")
    print("\nRows 5 to 10 of events_df:")
    print(events_df.iloc[5:11].to_string(index=False))"""


          

    
"""    if args.save:
        competitions_dict = get_competitions(creds=creds, fmt="dict")
        save_competitions_csv(competitions_dict, args.save)"""

if __name__ == "__main__":
    main()
