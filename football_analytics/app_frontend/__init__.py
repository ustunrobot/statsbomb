"""
Football Intelligence Frontend Application

A professional browser-based interface for generating Opposition and Player
reports using StatsBomb data integration.

This module provides the static frontend assets that are served by the Flask
backend application. The frontend communicates with the backend API to:
- Load competition, team, and player data
- Generate reports (Opposition and Player Reports)
- Monitor report generation progress
- Download generated PDF reports

Frontend Features:
    - Responsive design (desktop, tablet, mobile)
    - Real-time progress updates
    - Error handling and recovery
    - Accessibility compliant (WCAG 2.1 AA)
    - Cross-browser support
    - Dark mode support

Files:
    - index.html: Main HTML page with UI structure
    - styles.css: Complete CSS styling and responsive design
    - app.js: JavaScript logic for API integration and state management
    - README.md: Frontend documentation
    - __init__.py: Python package marker

Usage:
    This module is typically used by the Flask backend application:

    from flask import Flask
    app = Flask(__name__,
        static_folder='app_frontend',
        template_folder='app_frontend',
        static_url_path='/static'
    )

    # Serve static files
    @app.route('/')
    def index():
        return render_template('index.html')

API Endpoints Expected:
    - GET /api/competitions
    - GET /api/teams/<competition_id>
    - GET /api/players/<team_id>
    - POST /api/reports/opposition
    - POST /api/reports/player
    - GET /api/status/<task_id>
    - GET /api/reports/<task_id>/download

Author: Football Intelligence Development Team
Version: 1.0.0
"""

__version__ = '1.0.0'
__author__ = 'Football Intelligence Development Team'

# Frontend asset paths
STATIC_FILES = {
    'html': 'index.html',
    'css': 'styles.css',
    'js': 'app.js',
}

def get_static_file_path(file_type):
    """
    Get the path to a static frontend file.

    Args:
        file_type (str): Type of file ('html', 'css', 'js')

    Returns:
        str: Path to the static file
    """
    return STATIC_FILES.get(file_type.lower())

# Version info
VERSION_INFO = {
    'version': __version__,
    'name': 'Football Intelligence Frontend',
    'description': 'Browser-based UI for Opposition & Player Reports',
    'author': __author__,
}

def get_version_info():
    """Get version information for the frontend."""
    return VERSION_INFO.copy()
