#!/usr/bin/env python3
"""
Football Intelligence Application - Flask Backend

Main Flask application that serves the frontend and provides API endpoints
for competitions, teams, players, and report generation.
"""

import os
import sys
import json
import logging
import webbrowser
import threading
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file, make_response
from flask_cors import CORS
from dotenv import load_dotenv
import statsbombpy.sb as sb

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import backend services
from app_backend.statsbomb_service import get_service as get_statsbomb_service
from utils.data_loader import get_season_stats, get_player_season_data, get_team_data, fetch_events_with_360

# Configuration
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
PORT = int(os.getenv('PORT', 5000))
HOST = '127.0.0.1'  # Localhost only for security

# Create Flask app
frontend_path = Path(__file__).parent.parent / 'app_frontend'

app = Flask(
    __name__,
    static_folder=str(frontend_path),
    template_folder=str(frontend_path),
    static_url_path=''
)

logger.info(f"Frontend path: {frontend_path}")
logger.info(f"Static folder: {app.static_folder}")
logger.info(f"Template folder: {app.template_folder}")

# Enable CORS for localhost
CORS(app, origins=[f'http://{HOST}:{PORT}', 'http://localhost:5000'])

# Initialize services
statsbomb_service = get_statsbomb_service()

# ============================================================================
# ROUTES: Frontend
# ============================================================================

@app.route('/')
def index():
    """Serve main application page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving index: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load application'
        }), 500

@app.route('/static/<path:path>')
def static_files(path):
    """Serve static assets"""
    try:
        return send_file(f'app_frontend/{path}')
    except Exception as e:
        logger.error(f"Error serving static file: {e}")
        return jsonify({
            'status': 'error',
            'message': 'File not found'
        }), 404

# ============================================================================
# ROUTES: API - Competitions
# ============================================================================

@app.route('/api/competitions', methods=['GET'])
def get_competitions():
    """
    Get list of available competitions from StatsBomb API.

    Returns:
        JSON with competitions list containing:
        - id: competition_id
        - league: competition_name
        - season: season_name
        - country: country_name
        - year: extracted year
    """
    try:
        logger.info("Fetching competitions...")

        competitions = statsbomb_service.get_competitions(use_cache=True)

        return jsonify({
            'status': 'success',
            'data': competitions,
            'count': len(competitions)
        })

    except Exception as e:
        logger.error(f"Error fetching competitions: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch competitions: {str(e)}'
        }), 500

# ============================================================================
# ROUTES: API - Teams
# ============================================================================

@app.route('/api/teams/<int:competition_id>', methods=['GET'])
def get_teams(competition_id):
    """
    Get teams for a specific competition.

    Args:
        competition_id: StatsBomb competition ID

    Returns:
        JSON with teams list containing:
        - id: team_id
        - name: team_name
    """
    try:
        # Get season_id from query parameters or use latest
        season_id = request.args.get('season_id', type=int)

        if not season_id:
            # Get competitions to find season_id for this competition
            competitions = statsbomb_service.get_competitions(use_cache=True)
            comp_data = [c for c in competitions if c['id'] == competition_id]

            if not comp_data:
                return jsonify({
                    'status': 'error',
                    'message': f'Competition {competition_id} not found'
                }), 404

            # Use first (latest) season for this competition
            season_id = comp_data[0]['season_id']

        logger.info(f"Fetching teams for competition {competition_id}, season {season_id}...")

        teams = statsbomb_service.get_teams(competition_id, season_id, use_cache=True)

        return jsonify({
            'status': 'success',
            'data': teams,
            'count': len(teams)
        })

    except Exception as e:
        logger.error(f"Error fetching teams: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch teams: {str(e)}'
        }), 500

# ============================================================================
# ROUTES: API - Players
# ============================================================================

@app.route('/api/players/<int:team_id>', methods=['GET'])
def get_players(team_id):
    """
    Get players for a specific team.

    Query parameters:
        - competition_id: Required
        - season_id: Required

    Returns:
        JSON with players list containing:
        - id: player_id
        - name: player_name
        - number: shirt_number
    """
    try:
        competition_id = request.args.get('competition_id', type=int)
        season_id = request.args.get('season_id', type=int)

        if not competition_id or not season_id:
            return jsonify({
                'status': 'error',
                'message': 'competition_id and season_id are required'
            }), 400

        logger.info(f"Fetching players for team {team_id}...")

        players = statsbomb_service.get_players(
            competition_id,
            season_id,
            team_id,
            use_cache=True
        )

        return jsonify({
            'status': 'success',
            'data': players,
            'count': len(players)
        })

    except Exception as e:
        logger.error(f"Error fetching players: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch players: {str(e)}'
        }), 500

# ============================================================================
# ROUTES: API - Report Generation
# ============================================================================

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """
    Generate both team and player season stats reports.

    Request body:
        - competition_id: int (required)
        - season_id: int (required)
        - team_name: str (optional, for single team report)

    Returns:
        JSON with filepaths of both generated reports
    """
    try:
        data = request.get_json()

        competition_id = int(data.get('competition_id'))
        season_id = int(data.get('season_id'))
        team_name = data.get('team_name')

        if not competition_id or not season_id:
            return jsonify({
                'status': 'error',
                'message': 'competition_id and season_id are required'
            }), 400

        logger.info(f"Generating reports for competition {competition_id}, season {season_id}, team {team_name}")

        # Create data_temp directory
        data_temp_dir = Path(__file__).parent.parent / 'data_temp'
        data_temp_dir.mkdir(parents=True, exist_ok=True)

        # Get default credentials
        creds = {
            "user": "ustunrobot@gmail.com",
            "passwd": "waQMIar2",
        }

        # Generate both team and player season stats
        team_stats_filepath = get_season_stats(
            competition_id=competition_id,
            season_id=season_id,
            data_dir=str(data_temp_dir),
            team=team_name,
            creds=creds
        )

        player_stats_filepath = get_player_season_data(
            competition_id=competition_id,
            season_id=season_id,
            data_dir=str(data_temp_dir),
            team=team_name,
            creds=creds
        )

        logger.info(f"✓ Reports generated: Team={team_stats_filepath}, Players={player_stats_filepath}")

        return jsonify({
            'status': 'success',
            'team_stats_filepath': str(team_stats_filepath),
            'player_stats_filepath': str(player_stats_filepath),
            'message': f'Reports generated successfully'
        })

    except Exception as e:
        logger.error(f"Error generating reports: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate reports: {str(e)}'
        }), 500

@app.route('/api/reports/player-stats', methods=['POST'])
def generate_player_stats():
    """
    Generate both team and player season stats reports.

    Request body:
        - competition_id: int (required)
        - season_id: int (required)
        - team_name: str (optional, for single team report)

    Returns:
        JSON with filepaths of both generated reports
    """
    try:
        data = request.get_json()

        competition_id = int(data.get('competition_id'))
        season_id = int(data.get('season_id'))
        team_name = data.get('team_name')

        if not competition_id or not season_id:
            return jsonify({
                'status': 'error',
                'message': 'competition_id and season_id are required'
            }), 400

        logger.info(f"Generating reports for competition {competition_id}, season {season_id}, team {team_name}")

        # Create data_temp directory
        data_temp_dir = Path(__file__).parent.parent / 'data_temp'
        data_temp_dir.mkdir(parents=True, exist_ok=True)

        # Get default credentials
        creds = {
            "user": "ustunrobot@gmail.com",
            "passwd": "waQMIar2",
        }

        # Generate both team and player season stats
        team_stats_filepath = get_season_stats(
            competition_id=competition_id,
            season_id=season_id,
            data_dir=str(data_temp_dir),
            team=team_name,
            creds=creds
        )

        player_stats_filepath = get_player_season_data(
            competition_id=competition_id,
            season_id=season_id,
            data_dir=str(data_temp_dir),
            team=team_name,
            creds=creds
        )

        logger.info(f"✓ Reports generated: Team={team_stats_filepath}, Players={player_stats_filepath}")

        return jsonify({
            'status': 'success',
            'team_stats_filepath': str(team_stats_filepath),
            'player_stats_filepath': str(player_stats_filepath),
            'message': f'Reports generated successfully'
        })

    except Exception as e:
        logger.error(f"Error generating reports: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate reports: {str(e)}'
        }), 500

# ============================================================================
# ROUTES: API - Status
# ============================================================================

@app.route('/api/reports/team-events', methods=['GET', 'POST'])
def generate_team_events():
    """
    Generate event files for all matches of a team with progress tracking.

    Query/Request body parameters:
        - competition_id: int (required)
        - season_id: int (required)
        - team_name: str (required)

    Returns:
        Server-Sent Events stream with progress updates
    """
    # Extract parameters while still in request context
    if request.method == 'GET':
        competition_id = int(request.args.get('competition_id'))
        season_id = int(request.args.get('season_id'))
        team_name = request.args.get('team_name')
    else:
        data = request.get_json()
        competition_id = int(data.get('competition_id'))
        season_id = int(data.get('season_id'))
        team_name = data.get('team_name')

    def progress_stream():
        try:

            if not competition_id or not season_id or not team_name:
                yield f"data: {json.dumps({'status': 'error', 'message': 'Missing parameters'})}\n\n"
                return

            logger.info(f"Generating event files for team {team_name}")

            # Create data_temp directory
            data_temp_dir = Path(__file__).parent.parent / 'data_temp'
            data_temp_dir.mkdir(parents=True, exist_ok=True)

            # Get credentials
            creds = {
                "user": "ustunrobot@gmail.com",
                "passwd": "waQMIar2",
            }

            # Get season name from competitions API
            import statsbombpy.sb as sb_service
            competitions_df = sb_service.competitions(fmt="dataframe", creds=creds)
            season_row = competitions_df[(competitions_df['competition_id'] == competition_id) &
                                          (competitions_df['season_id'] == season_id)]
            season_name = str(season_row.iloc[0]['season_name']) if not season_row.empty else str(season_id)

            # Convert "/" to "-" in season name for folder naming
            season_folder_name = season_name.replace('/', '-')

            # Create team/season directory structure (do not clean)
            team_season_dir = data_temp_dir / "teams" / team_name / season_folder_name
            team_season_dir.mkdir(parents=True, exist_ok=True)

            # Get matches for team
            matches = sb.matches(competition_id=competition_id, season_id=season_id, creds=creds)
            team_matches = matches[(matches['home_team'] == team_name) | (matches['away_team'] == team_name)]

            # Filter out future matches - only include matches on or before today
            from datetime import datetime
            import pandas as pd
            today = pd.Timestamp(datetime.now().date())
            total_before_filter = len(team_matches)
            team_matches = team_matches[pd.to_datetime(team_matches['match_date']) <= today]
            total_after_filter = len(team_matches)

            if total_before_filter != total_after_filter:
                excluded = total_before_filter - total_after_filter
                logger.info(f"Date filter applied: Excluded {excluded} future matches")

            logger.info(f"Processing {len(team_matches)} matches (on or before {today.date()})")

            total_matches = len(team_matches)
            yield f"data: {json.dumps({'status': 'progress', 'total': total_matches, 'current': 0, 'percent': 0})}\n\n"

            # Download events for each match
            event_files = []
            for idx, (_, match) in enumerate(team_matches.iterrows(), 1):
                match_id = match['match_id']
                home = match['home_team']
                away = match['away_team']
                week = match['match_week']

                # Fetch events (includes 360 data in events)
                data_obj = fetch_events_with_360(match_id, creds=creds, include_360=True)
                events = data_obj["events"]

                # Save events
                filename = f"Week{week}_{home}_vs_{away}.json"
                filepath = team_season_dir / filename

                with open(filepath, 'w') as f:
                    json.dump(events, f, indent=2)
                event_files.append(str(filepath))

                # Send progress update
                percent = int((idx / total_matches) * 100)
                yield f"data: {json.dumps({'status': 'progress', 'total': total_matches, 'current': idx, 'percent': percent})}\n\n"

            # Final success response
            yield f"data: {json.dumps({'status': 'success', 'event_files': event_files, 'count': len(event_files), 'percent': 100})}\n\n"

        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return make_response(
        progress_stream(),
        200,
        {'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache'}
    )

@app.route('/api/reports/week-events', methods=['GET', 'POST'])
def generate_week_events():
    """
    Generate event files for all matches in a specific week with progress tracking.

    Query/Request body parameters:
        - competition_id: int (required)
        - season_id: int (required)
        - week_no: int (required)

    Returns:
        Server-Sent Events stream with progress updates
    """
    # Extract parameters while still in request context
    if request.method == 'GET':
        competition_id = int(request.args.get('competition_id'))
        season_id = int(request.args.get('season_id'))
        week_no = int(request.args.get('week_no'))
    else:
        data = request.get_json()
        competition_id = int(data.get('competition_id'))
        season_id = int(data.get('season_id'))
        week_no = int(data.get('week_no'))

    def progress_stream():
        try:

            if not competition_id or not season_id or not week_no:
                yield f"data: {json.dumps({'status': 'error', 'message': 'Missing parameters'})}\n\n"
                return

            logger.info(f"Generating event files for week {week_no}")

            # Create data_temp directory
            data_temp_dir = Path(__file__).parent.parent / 'data_temp'
            data_temp_dir.mkdir(parents=True, exist_ok=True)

            # Get credentials
            creds = {
                "user": "ustunrobot@gmail.com",
                "passwd": "waQMIar2",
            }

            # Get season name from competitions API
            import statsbombpy.sb as sb_service
            competitions_df = sb_service.competitions(fmt="dataframe", creds=creds)
            season_row = competitions_df[(competitions_df['competition_id'] == competition_id) &
                                          (competitions_df['season_id'] == season_id)]
            season_name = str(season_row.iloc[0]['season_name']) if not season_row.empty else str(season_id)

            # Convert "/" to "-" in season name for folder naming
            season_folder_name = season_name.replace('/', '-')

            # Get matches for the specific week
            matches = sb.matches(competition_id=competition_id, season_id=season_id, creds=creds)
            week_matches = matches[matches['match_week'] == week_no]

            # Filter out future matches
            from datetime import datetime
            import pandas as pd
            today = pd.Timestamp(datetime.now().date())
            total_before_filter = len(week_matches)
            week_matches = week_matches[pd.to_datetime(week_matches['match_date']) <= today]
            total_after_filter = len(week_matches)

            if total_before_filter != total_after_filter:
                excluded = total_before_filter - total_after_filter
                logger.info(f"Date filter applied: Excluded {excluded} future matches")

            logger.info(f"Processing {len(week_matches)} matches for week {week_no} (on or before {today.date()})")

            total_matches = len(week_matches)
            yield f"data: {json.dumps({'status': 'progress', 'total': total_matches, 'current': 0, 'percent': 0})}\n\n"

            # Download events for each match
            event_files = []
            for idx, (_, match) in enumerate(week_matches.iterrows(), 1):
                match_id = match['match_id']
                home = match['home_team']
                away = match['away_team']
                week = match['match_week']

                # Fetch events (includes 360 data in events)
                data_obj = fetch_events_with_360(match_id, creds=creds, include_360=True)
                events = data_obj["events"]

                # Save events for both home and away teams
                for team in [home, away]:
                    team_season_dir = data_temp_dir / "teams" / team / season_folder_name
                    team_season_dir.mkdir(parents=True, exist_ok=True)

                    filename = f"Week{week}_{home}_vs_{away}.json"
                    filepath = team_season_dir / filename

                    with open(filepath, 'w') as f:
                        json.dump(events, f, indent=2)
                    event_files.append(str(filepath))

                # Send progress update
                percent = int((idx / total_matches) * 100)
                yield f"data: {json.dumps({'status': 'progress', 'total': total_matches, 'current': idx, 'percent': percent})}\n\n"

            # Final success response
            yield f"data: {json.dumps({'status': 'success', 'event_files': event_files, 'count': len(event_files), 'percent': 100})}\n\n"

        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return make_response(
        progress_stream(),
        200,
        {'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache'}
    )

# ============================================================================
@app.route('/api/reports/opposition', methods=['POST'])
def generate_opposition_report():
    """
    Generate opposition intelligence report for a team in a season.

    Request body:
        - competition_id: int (required)
        - season_id: int (required)
        - team_id: int (required)
        - team_name: str (required)
        - season_name: str (required, e.g., "2025/2026")
        - league_name: str (required, e.g., "EFL League Two")

    Returns:
        JSON with path to generated report.html
    """
    import subprocess

    try:
        data = request.get_json()
        logger.info(f"Opposition report request data: {data}")

        # Extract and validate required parameters
        try:
            competition_id = int(data.get('competition_id'))
            season_id = int(data.get('season_id'))
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to parse competition_id or season_id: {e}")
            return jsonify({
                'status': 'error',
                'message': 'competition_id and season_id must be valid integers'
            }), 400

        team_name = data.get('team_name')
        season_name = data.get('season_name')
        league_name = data.get('league_name')

        logger.info(f"Extracted params - team: {team_name}, season: {season_name}, league: {league_name}, comp_id: {competition_id}, season_id: {season_id}")

        if not all([team_name, season_name, league_name, competition_id, season_id]):
            return jsonify({
                'status': 'error',
                'message': 'team_name, season_name, league_name, competition_id, and season_id are required'
            }), 400

        # Convert "/" to "-" in season name for compatibility
        season_name = season_name.replace('/', '-')

        logger.info(f"Generating opposition report for {team_name} in {season_name} ({league_name})")

        # Call run_report.py script
        run_report_path = Path(__file__).parent.parent / 'opposition_report' / 'run_report.py'

        # Execute the script with all parameters
        logger.info(f"Executing: python {run_report_path} '{team_name}' '{season_name}' '{league_name}' {competition_id} {season_id}")

        result = subprocess.run(
            ['python', str(run_report_path), team_name, season_name, league_name, str(competition_id), str(season_id)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        # Log all output from the subprocess
        if result.stdout:
            logger.info(f"run_report.py stdout:\n{result.stdout}")
        if result.stderr:
            logger.info(f"run_report.py stderr:\n{result.stderr}")

        if result.returncode != 0:
            logger.error(f"run_report.py failed with return code {result.returncode}: {result.stderr}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to generate opposition report: {result.stderr}'
            }), 500

        # Extract HTML from stdout if available
        html_content = None
        if result.stdout and '<<<HTML_START>>>' in result.stdout:
            try:
                start_idx = result.stdout.index('<<<HTML_START>>>') + len('<<<HTML_START>>>')
                end_idx = result.stdout.index('<<<HTML_END>>>')
                html_content = result.stdout[start_idx:end_idx].strip()
                logger.info(f"✓ Extracted HTML from stdout ({len(html_content)} bytes)")
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to extract HTML from stdout: {e}")

        # Report should also be saved to opposition_report/report.html
        report_path = Path(__file__).parent.parent / 'opposition_report' / 'report.html'

        if not report_path.exists():
            logger.warning(f"Report file not found at {report_path}, but HTML may be available in response")

        logger.info(f"✓ Opposition report generated: {report_path}")

        return jsonify({
            'status': 'success',
            'report_filepath': str(report_path),
            'html_content': html_content,  # Direct HTML for frontend display
            'message': f'Opposition report generated successfully for {team_name}',
            'debug': {
                'stdout': result.stdout[-500:] if result.stdout else '',  # Last 500 chars
                'stderr': result.stderr[-500:] if result.stderr else ''
            }
        })

    except subprocess.TimeoutExpired:
        logger.error("Report generation timed out")
        return jsonify({
            'status': 'error',
            'message': 'Report generation timed out after 5 minutes'
        }), 504

    except Exception as e:
        logger.error(f"Error generating opposition report: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Error generating opposition report: {str(e)}'
        }), 500


# ROUTES: API - Status
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Football Intelligence API is running'
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({
        'status': 'error',
        'message': 'An unexpected error occurred'
    }), 500

# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

def open_browser():
    """Open browser to localhost after short delay"""
    threading.Timer(2.0, lambda: webbrowser.open(f'http://{HOST}:{PORT}')).start()

def print_banner():
    """Print welcome banner"""
    banner = f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║     Football Intelligence Application                     ║
    ║                                                           ║
    ║  Server running on: http://{HOST}:{PORT}                ║
    ║  Opening browser in 2 seconds...                         ║
    ║                                                           ║
    ║  Press Ctrl+C to stop the application                    ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

if __name__ == '__main__':
    try:
        print_banner()

        # Open browser
        open_browser()

        # Run Flask server
        logger.info(f"Starting Flask server on {HOST}:{PORT}")
        app.run(
            host=HOST,
            port=PORT,
            debug=DEBUG,
            use_reloader=False,  # Important for PyInstaller
            use_debugger=False,
        )

    except KeyboardInterrupt:
        print("\n\n✓ Application stopped gracefully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n✗ Error: {e}")
        sys.exit(1)
