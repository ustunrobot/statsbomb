#!/usr/bin/env python3
"""Section 12: Player median reception positions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.metrics import Metric


def get_styles() -> str:
    """Return CSS styles for section 12."""
    return """
    <style>
    .s12-median-positions-section {
      padding: 40px 48px;
      background: white;
      border-top: 1px solid #e5e5e5;
    }

    .s12-section-container {
      max-width: 1000px;
    }

    .s12-section-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 24px;
      font-weight: 700;
      color: #0f1923;
      margin-bottom: 4px;
    }

    .s12-section-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: #999;
      margin-bottom: 24px;
    }

    .s12-median-positions-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 32px;
      margin-bottom: 32px;
    }

    .s12-position-card {
      display: flex;
      flex-direction: column;
    }

    .s12-position-card-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 14px;
      font-weight: 600;
      color: #0f1923;
      margin-bottom: 8px;
    }

    .s12-subsection-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 16px;
      font-weight: 600;
      color: #0f1923;
      margin-top: 32px;
      margin-bottom: 4px;
    }

    .s12-player-stats {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 11px;
      color: #666;
      margin-top: 8px;
      padding: 12px;
      background: #f9f9f9;
      border-radius: 6px;
    }

    .s12-player-stat-item {
      display: flex;
      justify-content: space-between;
      margin-bottom: 6px;
    }

    .s12-player-stat-item:last-child {
      margin-bottom: 0;
    }

    .s12-player-stat-label {
      color: #999;
    }

    .s12-player-stat-value {
      font-weight: 600;
      color: #333;
    }

    .s12-median-positions-svg {
      width: auto;
      height: auto;
      display: block;
      margin-top: 16px;
    }

    .s12-player-name-label {
      font-size: 9px;
      font-weight: 500;
      fill: #fff;
      text-anchor: middle;
    }
    </style>
    """


def extract_player_positions(team_metrics: dict, all_player_stats: dict = None) -> dict:
    """
    Extract player median positions from team metrics.

    Returns a dictionary mapping player_id to {median_x, median_y, reception_count, player_number, name, jersey_number, minutes}
    """
    players = {}
    player_metadata = team_metrics.get('player_metadata', {})

    # Build player minutes lookup from all_player_stats
    player_minutes = {}
    if all_player_stats:
        for player_id, player_data in all_player_stats.items():
            if isinstance(player_data, dict):
                minutes = player_data.get('player_season_minutes', 0)
                player_minutes[player_id] = minutes

    # Extract all player metrics from the team_metrics dictionary
    for key, metric in team_metrics.items():
        if not isinstance(metric, Metric):
            continue

        # Parse player-related metrics
        if key.startswith('player_') and '_median_x' in key:
            # Extract player_id from key like "player_123_median_x"
            parts = key.split('_')
            if len(parts) >= 3:
                try:
                    player_id = int(parts[1])
                    if player_id not in players:
                        players[player_id] = {
                            'player_id': player_id,
                            'median_x': 0.0,
                            'median_y': 0.0,
                            'reception_count': 0,
                        }
                    players[player_id]['median_x'] = metric.value
                except (ValueError, IndexError):
                    pass

        elif key.startswith('player_') and '_median_y' in key:
            parts = key.split('_')
            if len(parts) >= 3:
                try:
                    player_id = int(parts[1])
                    if player_id not in players:
                        players[player_id] = {
                            'player_id': player_id,
                            'median_x': 0.0,
                            'median_y': 0.0,
                            'reception_count': 0,
                        }
                    players[player_id]['median_y'] = metric.value
                except (ValueError, IndexError):
                    pass

        elif key.startswith('player_') and '_reception_count' in key:
            parts = key.split('_')
            if len(parts) >= 3:
                try:
                    player_id = int(parts[1])
                    if player_id not in players:
                        players[player_id] = {
                            'player_id': player_id,
                            'median_x': 0.0,
                            'median_y': 0.0,
                            'reception_count': 0,
                        }
                    players[player_id]['reception_count'] = int(metric.value)
                except (ValueError, IndexError):
                    pass

    # Filter out players with no receptions and assign player numbers
    filtered_players = {}
    for player_id, player_data in players.items():
        if player_data['reception_count'] > 0:
            # Get metadata if available
            metadata = player_metadata.get(player_id, {})
            player_data['player_number'] = metadata.get('jersey_number', player_id % 100 if player_id > 100 else player_id)
            player_data['name'] = metadata.get('name', f"Player {player_id}")
            # Add minutes played for filtering
            player_data['minutes'] = player_minutes.get(player_id, 0)
            filtered_players[player_id] = player_data

    return filtered_players


def create_median_positions_pitch(players: dict, passes_dict: dict = None) -> str:
    """Create SVG pitch with player median reception positions (top 11 by minutes played) and passing network."""
    if not players:
        return '<p style="color: #999; font-style: italic;">No player reception data available.</p>'

    # Filter to show only top 11 players by minutes played to represent the most common formation
    sorted_players = sorted(players.items(), key=lambda x: x[1].get('minutes', 0), reverse=True)
    top_11_players = dict(sorted_players[:11])
    top_11_player_ids = set(top_11_players.keys())

    if not top_11_players:
        return '<p style="color: #999; font-style: italic;">No player reception data available.</p>'

    # Pitch dimensions
    pitch_width = 520
    pitch_height = int(pitch_width * (80 / 120))  # 347px

    # Padding around the pitch
    padding = 20
    total_width = pitch_width + padding * 2
    total_height = pitch_height + padding * 2

    # Create coordinate mapping function: pitch coords (0-120, 0-80) to SVG coords
    def pitch_to_svg(x, y):
        svg_x = padding + (x / 120) * pitch_width
        svg_y = padding + (y / 80) * pitch_height
        return (svg_x, svg_y)

    # Calculate reception count range for scaling circle size
    reception_counts = [p['reception_count'] for p in top_11_players.values()]
    min_count = min(reception_counts) if reception_counts else 1
    max_count = max(reception_counts) if reception_counts else 1

    # Calculate pitch markings dimensions
    px_per_unit_w = pitch_width / 120
    px_per_unit_h = pitch_height / 80

    penalty_width = int(22 * px_per_unit_w)
    penalty_height = int(36 * px_per_unit_h)
    goal_width = int(9 * px_per_unit_w)
    goal_height = int(12 * px_per_unit_h)

    center_y = pitch_height // 2
    penalty_y = int(center_y - penalty_height / 2)
    goal_y = int(center_y - goal_height / 2)

    # Draw pitch background
    svg = f"""
    <svg width="{total_width}" height="{total_height}" viewBox="0 0 {total_width} {total_height}" xmlns="http://www.w3.org/2000/svg" class="s12-median-positions-svg">
        <!-- Pitch background -->
        <rect x="{padding}" y="{padding}" width="{pitch_width}" height="{pitch_height}" fill="#2d5a2d" stroke="#fff" stroke-width="2"/>

        <!-- Halfway line -->
        <line x1="{padding + pitch_width//2}" y1="{padding}" x2="{padding + pitch_width//2}" y2="{padding + pitch_height}" stroke="#fff" stroke-width="1"/>

        <!-- Center circle -->
        <circle cx="{padding + pitch_width//2}" cy="{padding + pitch_height//2}" r="{int(10*px_per_unit_w)}" fill="none" stroke="#fff" stroke-width="1"/>

        <!-- Center spot -->
        <circle cx="{padding + pitch_width//2}" cy="{padding + pitch_height//2}" r="2" fill="#fff"/>

        <!-- Left penalty area -->
        <rect x="{padding}" y="{padding + penalty_y}" width="{penalty_width}" height="{penalty_height}" fill="none" stroke="#fff" stroke-width="1"/>

        <!-- Right penalty area -->
        <rect x="{padding + pitch_width - penalty_width}" y="{padding + penalty_y}" width="{penalty_width}" height="{penalty_height}" fill="none" stroke="#fff" stroke-width="1"/>

        <!-- Left goal area -->
        <rect x="{padding}" y="{padding + goal_y}" width="{goal_width}" height="{goal_height}" fill="none" stroke="#fff" stroke-width="1"/>

        <!-- Right goal area -->
        <rect x="{padding + pitch_width - goal_width}" y="{padding + goal_y}" width="{goal_width}" height="{goal_height}" fill="none" stroke="#fff" stroke-width="1"/>
    """

    # Draw pass connections between players (before drawing player circles)
    if passes_dict:
        # Parse and combine bidirectional passes between player pairs
        pass_pairs = {}  # Key: (min_id, max_id), Value: total count

        for key, count in passes_dict.items():
            # Handle both dict and tuple key formats
            if isinstance(key, str):
                try:
                    passer_id, receiver_id = map(int, key.strip('()').split(','))
                except (ValueError, AttributeError):
                    continue
            else:
                passer_id, receiver_id = key

            # Only include passes between the top 11 players
            if passer_id in top_11_player_ids and receiver_id in top_11_player_ids:
                # Create a normalized key (always smaller id first) for bidirectional pairs
                pair_key = (min(passer_id, receiver_id), max(passer_id, receiver_id))
                pass_pairs[pair_key] = pass_pairs.get(pair_key, 0) + count

        # Convert to list format for processing
        pass_data_list = []
        for (player1_id, player2_id), total_count in pass_pairs.items():
            pass_data_list.append({
                'passer_id': player1_id,
                'receiver_id': player2_id,
                'count': total_count
            })

        if pass_data_list:
            # Sort all passes by count descending
            sorted_all_passes = sorted(pass_data_list, key=lambda p: p['count'], reverse=True)

            # Keep only top 4 passes per player (limit connections involving each player)
            player_connection_count = {}
            filtered_pass_data = []

            for pass_conn in sorted_all_passes:
                passer_id = pass_conn['passer_id']
                receiver_id = pass_conn['receiver_id']

                # Count connections for both players
                passer_count = player_connection_count.get(passer_id, 0)
                receiver_count = player_connection_count.get(receiver_id, 0)

                # Only add if both players have less than 4 connections
                if passer_count < 4 and receiver_count < 4:
                    filtered_pass_data.append(pass_conn)
                    player_connection_count[passer_id] = passer_count + 1
                    player_connection_count[receiver_id] = receiver_count + 1

            # Calculate pass count range for line width scaling
            pass_counts = [p['count'] for p in filtered_pass_data]
            min_passes = min(pass_counts) if pass_counts else 1
            max_passes = max(pass_counts) if pass_counts else 1

            # Find top 5 highest pass counts for color highlighting
            sorted_passes = sorted(filtered_pass_data, key=lambda p: p['count'], reverse=True)
            top_5_indices = set()
            for i in range(min(5, len(sorted_passes))):
                top_5_indices.add(id(sorted_passes[i]))

            # Draw pass connections
            for pass_conn in filtered_pass_data:
                passer_id = pass_conn['passer_id']
                receiver_id = pass_conn['receiver_id']
                count = pass_conn['count']

                if passer_id in top_11_players and receiver_id in top_11_players:
                    passer_pos = top_11_players[passer_id]
                    receiver_pos = top_11_players[receiver_id]

                    x1, y1 = pitch_to_svg(passer_pos['median_x'], passer_pos['median_y'])
                    x2, y2 = pitch_to_svg(receiver_pos['median_x'], receiver_pos['median_y'])

                    # Scale line width by pass count (1-5px range)
                    line_width = 1 + (count - min_passes) / (max_passes - min_passes) * 4 if max_passes > min_passes else 1

                    # Use bright yellow for top 5 pass counts, gold for others
                    line_color = "#ffdc53" if id(pass_conn) in top_5_indices else "#D4A017"

                    svg += f'        <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{line_color}" stroke-width="{line_width}" opacity="0.8"/>\n'

    # Draw players at median reception positions (top 11 only)
    for player_id, player_data in sorted(top_11_players.items(), key=lambda x: x[1]['reception_count'], reverse=True):
        x = player_data['median_x']
        y = player_data['median_y']
        count = player_data['reception_count']
        number = player_data['player_number']
        name = player_data.get('name', 'Unknown')

        # Clamp coordinates to pitch bounds
        x = max(0, min(120, x))
        y = max(0, min(80, y))

        svg_x, svg_y = pitch_to_svg(x, y)

        # Scale circle radius by reception count (8-20px range)
        radius = 8 + (count - min_count) / (max_count - min_count) * 12 if max_count > min_count else 8

        svg += f'        <circle cx="{svg_x}" cy="{svg_y}" r="{radius}" fill="#9B552D" stroke="#fff" stroke-width="2"/>\n'
        svg += f'        <text x="{svg_x}" y="{svg_y}" text-anchor="middle" dominant-baseline="middle" font-size="11" font-weight="700" fill="#fff" font-family="Inter, system-ui, sans-serif">{number}</text>\n'

        # Extract short name (first initial + full last name)
        name_parts = name.split()
        if len(name_parts) >= 2:
            short_name = f"{name_parts[0][0]} {name_parts[-1]}"
        else:
            short_name = name if name else "N/A"

        # Add name label below circle (with offset for readability)
        label_y = svg_y + radius + 12
        svg += f'        <text x="{svg_x}" y="{label_y}" class="s12-player-name-label">{short_name}</text>\n'

    svg += '    </svg>\n'
    return svg


def render_median_positions_section(team_metrics: dict, team_name: str, all_player_stats: dict = None) -> str:
    """
    Render player median reception positions section with passing network.

    Args:
        team_metrics: Team metrics from event data
        team_name: Name of the team
        all_player_stats: Dictionary of all player stats (keyed by player_id) for filtering by minutes

    Returns:
        HTML string for the section
    """
    players = extract_player_positions(team_metrics, all_player_stats)

    # Sort players by reception count (descending)
    sorted_players = sorted(players.items(), key=lambda x: x[1]['reception_count'], reverse=True)

    # Get passing matrix data
    passing_matrix_data = team_metrics.get('passing_matrix_data', {})
    passes_dict = passing_matrix_data.get('passes', {})

    # Create pitch visualization
    pitch_svg = create_median_positions_pitch(players, passes_dict)

    html = f"""
    <div class="s12-median-positions-section">
        <div class="s12-section-container">            
            <p class="s12-section-subtitle">Median positions and passing networks for {team_name}</p>            
            {pitch_svg}            
        </div>
    </div>
    """

    return html
