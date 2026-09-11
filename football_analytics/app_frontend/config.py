"""
Frontend Configuration

Configuration settings for integrating the frontend with the Flask backend.
This file provides constants and settings that bridge the frontend and backend.
"""

import os
from pathlib import Path

# ============================================================================
# Paths
# ============================================================================

# Get the directory where this file is located
FRONTEND_DIR = Path(__file__).parent.absolute()

# Frontend file paths
FRONTEND_FILES = {
    'index': FRONTEND_DIR / 'index.html',
    'styles': FRONTEND_DIR / 'styles.css',
    'script': FRONTEND_DIR / 'app.js',
}

# Assets directory (for images, icons, etc.)
ASSETS_DIR = FRONTEND_DIR / 'assets'

# ============================================================================
# Flask Configuration
# ============================================================================

# Frontend serving configuration for Flask
FLASK_CONFIG = {
    'static_folder': str(FRONTEND_DIR),
    'template_folder': str(FRONTEND_DIR),
    'static_url_path': '/static',
}

# ============================================================================
# API Configuration
# ============================================================================

# Frontend API endpoints configuration
API_CONFIG = {
    'base_url': 'http://localhost:5000/api',
    'timeout': 30000,  # milliseconds
    'poll_interval': 2000,  # milliseconds
}

# Expected API endpoints
API_ENDPOINTS = {
    'competitions': '/competitions',
    'teams': '/teams/{competition_id}',
    'players': '/players/{team_id}',
    'generate_opposition': '/reports/opposition',
    'generate_player': '/reports/player',
    'status': '/status/{task_id}',
    'download': '/reports/{task_id}/download',
}

# ============================================================================
# UI Configuration
# ============================================================================

# Default UI settings
UI_CONFIG = {
    'theme': 'light',  # 'light', 'dark', or 'auto'
    'language': 'en',
    'animations_enabled': True,
    'accessibility_mode': False,
}

# Color scheme
COLORS = {
    'primary': '#1e40af',
    'secondary': '#06b6d4',
    'success': '#10b981',
    'error': '#ef4444',
    'warning': '#f59e0b',
    'text_dark': '#1f2937',
    'text_light': '#6b7280',
    'bg_light': '#f9fafb',
    'bg_white': '#ffffff',
}

# ============================================================================
# Report Configuration
# ============================================================================

REPORT_CONFIG = {
    'types': {
        'opposition': {
            'name': 'Opposition Report',
            'description': 'Comprehensive analysis of the team as opposition',
            'icon': '📊',
        },
        'player': {
            'name': 'Player Report',
            'description': 'Individual player performance analysis',
            'icon': '👤',
        },
    },
    'timeout_seconds': 300,  # 5 minutes max generation time
}

# ============================================================================
# Feature Flags
# ============================================================================

FEATURES = {
    'enable_dark_mode': True,
    'enable_i18n': False,  # Internationalization
    'enable_offline_mode': False,
    'enable_batch_generation': False,
    'enable_report_history': False,
    'enable_user_accounts': False,
}

# ============================================================================
# Validation Configuration
# ============================================================================

VALIDATION = {
    'min_competition_name_length': 1,
    'max_competition_name_length': 100,
    'min_team_name_length': 1,
    'max_team_name_length': 100,
    'min_player_name_length': 1,
    'max_player_name_length': 100,
}

# ============================================================================
# Performance Configuration
# ============================================================================

PERFORMANCE = {
    'cache_duration_ms': 3600000,  # 1 hour
    'debounce_duration_ms': 300,  # 300ms for input events
    'animation_duration_ms': 300,  # CSS animation duration
}

# ============================================================================
# Logging Configuration
# ============================================================================

LOGGING = {
    'enabled': True,
    'level': 'info',  # 'debug', 'info', 'warn', 'error'
    'log_api_calls': True,
    'log_state_changes': True,
    'log_errors': True,
}

# ============================================================================
# Helper Functions
# ============================================================================

def get_frontend_file_path(file_type):
    """
    Get absolute path to a frontend file.

    Args:
        file_type (str): 'index', 'styles', or 'script'

    Returns:
        Path: Absolute path to the file
    """
    return FRONTEND_FILES.get(file_type)

def get_api_endpoint(endpoint_name, **kwargs):
    """
    Get a formatted API endpoint URL.

    Args:
        endpoint_name (str): Name of the endpoint
        **kwargs: Format variables for the endpoint

    Returns:
        str: Full API endpoint URL

    Example:
        >>> get_api_endpoint('teams', competition_id=5)
        'http://localhost:5000/api/teams/5'
    """
    endpoint = API_ENDPOINTS.get(endpoint_name)
    if not endpoint:
        raise ValueError(f"Unknown endpoint: {endpoint_name}")

    if kwargs:
        endpoint = endpoint.format(**kwargs)

    return API_CONFIG['base_url'] + endpoint

def is_feature_enabled(feature_name):
    """
    Check if a feature is enabled.

    Args:
        feature_name (str): Name of the feature

    Returns:
        bool: True if enabled, False otherwise
    """
    return FEATURES.get(f'enable_{feature_name}', False)

def get_report_config(report_type):
    """
    Get configuration for a report type.

    Args:
        report_type (str): 'opposition' or 'player'

    Returns:
        dict: Report configuration
    """
    return REPORT_CONFIG['types'].get(report_type, {})

# ============================================================================
# Export public API
# ============================================================================

__all__ = [
    'FRONTEND_DIR',
    'FRONTEND_FILES',
    'ASSETS_DIR',
    'FLASK_CONFIG',
    'API_CONFIG',
    'API_ENDPOINTS',
    'UI_CONFIG',
    'COLORS',
    'REPORT_CONFIG',
    'FEATURES',
    'VALIDATION',
    'PERFORMANCE',
    'LOGGING',
    'get_frontend_file_path',
    'get_api_endpoint',
    'is_feature_enabled',
    'get_report_config',
]
