"""
Visualization utilities for football analytics.

Functions for plotting match events and statistics on a football pitch.
"""

from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from collections import deque

def find_shape_from_ball_receipts(events: pd.DataFrame, team: str, filter: str = None) -> Dict:
    """
    Determine team shape from Ball Receipt locations in their own half (all events, not just buildups).

    Args:
        events: DataFrame of all match events
        team: Team name to analyze

    Returns:
        Dict with shape analysis including:
        - back_shape: "3 Back", "4 Back", or "Unknown"
        - back_shape_confidence: 0.0-1.0 confidence score
        - medians: Dict with position-level median x,y locations and counts
    """
    ret = {}

    # Filter to team's events
    team_events = events[events['team_name'] == team].copy() if 'team_name' in events.columns else events[events['team'] == team].copy()

    if team_events.empty:
        print(f"No events found for team: {team}")
        return ret

    # Filter to Ball Receipt* events in own half (x < 60)
    ball_receipt_events = team_events[
        (team_events['type_name'] == 'Ball Receipt*') &
        (team_events['x'] < 60)
    ].copy()

    if ball_receipt_events.empty:
        print(f"No Ball Receipt events in own half for team: {team}")
        return ret

    # Collect locations by position
    positions_data = {}
    all_touches = {}

    for _, event in ball_receipt_events.iterrows():
        position = event.get('position') if isinstance(event, dict) else getattr(event, 'position', None)

        if not position or pd.isna(position):
            continue

        x = event.get('x') if isinstance(event, dict) else getattr(event, 'x', None)
        y = event.get('y') if isinstance(event, dict) else getattr(event, 'y', None)

        if pd.isna(x) or pd.isna(y):
            continue

        if filter:
            if filter not in position:
                continue
        
        location = {"x": x, "y": y}

        if position not in all_touches:
            all_touches[position] = []
        all_touches[position].append(location)

        if position not in positions_data:
            positions_data[position] = {'x': [], 'y': [], 'count': 0}

        positions_data[position]['x'].append(x)
        positions_data[position]['y'].append(y)
        positions_data[position]['count'] += 1

    if not positions_data:
        print(f"No valid position data found in own half")
        return ret

    # Determine back shape from Centre Back distribution
    shape, confidence = find_back_shape(positions_data)
    ret["back_shape"] = shape
    ret["back_shape_confidence"] = confidence

    # Calculate medians and filter by minimum count
    medians = {}
    min_count = 10  # Minimum number of events to include

    for position, data in positions_data.items():
        if data['count'] < min_count:
            continue
        median_x = pd.Series(data['x']).median()
        median_y = pd.Series(data['y']).median()
        medians[position] = {
            'x': median_x,
            'y': median_y,
            'count': data['count']
        }

    if not medians:
        print(f"No positions with >= {min_count} ball receipts in own half")
        return ret

    print(f"\nMedian locations by position in own half (n >= {min_count}):")
    print("=" * 70)
    for position in sorted(medians.keys()):
        m = medians[position]
        print(f"{position:25} | X: {m['x']:6.1f}, Y: {m['y']:6.1f} (n={m['count']:3d})")

    ret["medians"] = medians
    ret["all_touches"] = all_touches
    return ret



def find_back_shape(positions_data: Dict) -> Tuple[str, float]:
    """
    Determine defensive back shape based on Centre Back ball receipt distribution.

    Args:
        positions_data: Dict with position names as keys and {'count': int} as values

    Returns:
        Tuple of (shape: str, confidence: float)
        - shape: "3 Back", "4 Back", or "Unknown"
        - confidence: Score 0.0-1.0 indicating how well the data fits the shape
    """
    # Extract Centre Back positions and their counts
    cb_positions = {
        'Left Center Back': 0,
        'Right Center Back': 0,
        'Center Back': 0,
    }

    for position, data in positions_data.items():
        if 'Center Back' in position:
            # Match against our known positions
            for cb_pos in cb_positions.keys():
                if position == cb_pos:
                    cb_positions[cb_pos] = data['count']

    print(f"\nCenter Back distribution:")
    total = sum(cb_positions.values())
    for position, count in cb_positions.items():
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {position}: {count} ({pct:.1f}%)")


    min_pos_count = min(cb_positions['Left Center Back'], cb_positions['Right Center Back'])

    if min_pos_count == 0:
        return "Unknown", 0.0

    ratio = (cb_positions['Center Back'] / min_pos_count)
    if ratio > 0.5:
        shape = "3 Back"
        if ratio > 0.8:
            confidence = 1.0
        elif ratio > 0.6:
            confidence = 0.8
        else:
            confidence = 0.6
    else:
        shape = "4 Back"
        if ratio > 0.2:
            confidence = 0.8
        else:
            confidence = 0.95

    print(f"Back shape: {shape} (confidence: {confidence:.2f})")

    return shape, confidence
   

def find_shape(buildups: List[Dict]) -> Dict:
    ret = {}
    # Helper function to get values from dict or namedtuple
    def get_value(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        else:
            return getattr(obj, key, default)

    # Collect locations by position and buildup end locations
    positions_data = {}
    gk_involvement = 0 # how many time the goalkeeper received in the buildup, excluding the first pass
    buildup_end_locations = {'left': 0, 'center': 0, 'right': 0}
    backward_passes_by_position = {}  # Track backward passes by position
    last_three_positions = []
    for buildup in buildups:
        events = buildup.get('events', []) if isinstance(buildup, dict) else getattr(buildup, 'buildups', [])
        gk_name = buildup.get('gk_name')
        # Track buildup end location (from last event's y coordinate)
        if events:
            last_event = events[-1] 
            end_y = get_value(last_event, 'y')
            if pd.notna(end_y):
                # Pitch width = 80, divide into thirds: left (0-26.7), center (26.7-53.3), right (53.3-80)
                if end_y < 26.7:
                    buildup_end_locations['left'] += 1
                elif end_y > 53.3:
                    buildup_end_locations['right'] += 1
                else:
                    buildup_end_locations['center'] += 1

        ball_receipt_no = 0
        last_three = deque(maxlen=3)
        for event in events:
            # Filter by event type
            event_type_val = get_value(event, 'type_name')
            if event_type_val not in ("Ball Receipt*", "Pass"):
                continue

            if event_type_val == "Pass" and get_value(event, 'recipient') != gk_name:
                # Track backward passes (where end_x < start_x)
                start_x = get_value(event, 'x')
                pass_end_x = get_value(event, 'pass_end_x')
                position = get_value(event, 'position')

                if pd.notna(start_x) and pd.notna(pass_end_x) and position:
                    if pass_end_x < start_x:  # Backward pass
                        if position not in backward_passes_by_position:
                            backward_passes_by_position[position] = 0
                        backward_passes_by_position[position] += 1

                continue

            ball_receipt_no += 1

            position = get_value(event, 'position')            
            if not position or pd.isna(position):
                continue

            last_three.append(position)

            if position == "Goalkeeper" and ball_receipt_no > 1:
                gk_involvement += 1 

            x = get_value(event, 'x')
            y = get_value(event, 'y')
            if pd.notna(x) and pd.notna(y):
                if position not in positions_data:
                    positions_data[position] = {'x': [], 'y': [], 'count': 0}
                positions_data[position]['x'].append(x)
                positions_data[position]['y'].append(y)
                positions_data[position]['count'] += 1

        if buildup.get('outcome') == 'success' and len(last_three) == 3:
            last_three_positions.append(last_three)

    if not positions_data:
        print(f"No events found")
        return ret

    shape, confidence = find_back_shape(positions_data)
    ret["back_shape"] = shape
    ret["back_shape_confidence"] = confidence
    ret["gk_involvement"] = gk_involvement / len(buildups)

    buildup_combinations(last_three_positions, shape)

    # Calculate buildup end location percentages
    total_buildups = sum(buildup_end_locations.values())
    if total_buildups > 0:
        ret["buildup_end_left"] = buildup_end_locations['left'] / total_buildups
        ret["buildup_end_center"] = buildup_end_locations['center'] / total_buildups
        ret["buildup_end_right"] = buildup_end_locations['right'] / total_buildups
        print(f"\nBuildup end locations:")
        print(f"  Left: {buildup_end_locations['left']} ({ret['buildup_end_left']*100:.1f}%)")
        print(f"  Center: {buildup_end_locations['center']} ({ret['buildup_end_center']*100:.1f}%)")
        print(f"  Right: {buildup_end_locations['right']} ({ret['buildup_end_right']*100:.1f}%)")
    else:
        ret["buildup_end_left"] = 0.0
        ret["buildup_end_center"] = 0.0
        ret["buildup_end_right"] = 0.0

    # Find top 2 backward passes by position
    if backward_passes_by_position:
        top_2_backward = sorted(backward_passes_by_position.items(), key=lambda x: x[1], reverse=True)[:2]
        print(f"\nTop 2 positions making backward passes:")
        for i, (position, count) in enumerate(top_2_backward, 1):
            ret[f"backward_pass_position_{i}"] = position
            ret[f"backward_pass_count_{i}"] = count
            print(f"  {i}. {position}: {count}")
    else:
        ret["backward_pass_position_1"] = "N/A"
        ret["backward_pass_count_1"] = 0
        ret["backward_pass_position_2"] = "N/A"
        ret["backward_pass_count_2"] = 0

    # Calculate medians and filter by minimum count
    medians = {}
    min_count = 25  # Minimum number of events to include

    for position, data in positions_data.items():
        if data['count'] < min_count:
            continue
        median_x = pd.Series(data['x']).median()
        median_y = pd.Series(data['y']).median()
        medians[position] = {
            'x': median_x,
            'y': median_y,
            'count': data['count']
        }

    if not medians:
        print(f"No positions with >= {min_count} events found")
        return ret

    print(f"\nMedian locations by position (n >= {min_count}):")
    print("=" * 70)
    for position in sorted(medians.keys()):
        m = medians[position]
        print(f"{position:25} | X: {m['x']:6.1f}, Y: {m['y']:6.1f} (n={m['count']:3d})")

    ret["medians"] = medians
    return ret

def buildup_combinations(positions: List, back_shape: str) -> None:

    list_comb = {}

    for pos in positions:
        combination = position_group(pos[0], back_shape) + "->" + position_group(pos[1], back_shape) + "->" + position_group(pos[2], back_shape)
        list_comb[combination] = list_comb.get(combination, 0) + 1

    top_3 = sorted(list_comb.items(), key=lambda x: x[1], reverse=True)[:3]
    print("Most repeating combinations:")
    print(top_3)

def position_group(position: str, back_shape: str) -> str:

    if position == "Goalkeeper":
        return "GK"
    if "Center Back" in position:
        return "CB"
    if "Back" in position:
        if back_shape == "3 Back":
            return "WB"
        else:
            return "FB"
    if "Defensive Midfield" in position:
        return "DM"
    if "Attacking Midfield" in position:
        return "AM"
    if "Midfield" in position:
        return "M"
    if "Wing" in position:
        return "W"
    if "Forward" in position:
        return "FWD"
    return position

def visualize_touch(touches_by_position: dict, title: str = "Touch Locations") -> None:
    """
    Visualize touch locations by position with different colors for each position.

    Args:
        touches_by_position: Dict with position names as keys and list of location dicts as values
        title: Title for the visualization and filename
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
    except ImportError:
        print("matplotlib required for visualization. Install with: pip install matplotlib")
        return

    if not touches_by_position:
        print("No locations to visualize")
        return

    # Color map for positions
    colors_map = {
        'Goalkeeper': "#737070",
        'Right Center Back': '#FF0000',
        'Left Center Back': "#006AFF",
        'Right Back': "#484648",
        'Left Back': "#0B0B0B",
        'Right Defensive Midfield': "#409F08",
        'Center Defensive Midfield': "#A212D6",
        'Left Defensive Midfield': "#AB820A",
        'Right Attacking Midfield': '#00FFFF',
        'Left Attacking Midfield': '#FFFF00',
        'Right Midfield': '#FF3333',
        'Left Midfield': '#33FF33',
        'Right Wing': '#3333FF',
        'Left Wing': '#FFFF33',
        'Right Forward': '#FF33FF',
        'Left Forward': '#33FFFF',
        'Center Forward': '#FF9900',
        'Defensive Midfield': '#6666FF',
        'Attacking Midfield': '#FF6666',
        'Midfield': '#66FF66',
        'Wing': '#FFFF66',
        'Forward': '#FF66FF',
    }

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(16, 12))

    # Draw football pitch with teal stripes for realistic look
    stripe_width = 10
    colors_stripes = ["#E6F4EA", "#C0DECD"]
    for i in range(0, 120, stripe_width):
        color = colors_stripes[(i // stripe_width) % 2]
        stripe = patches.Rectangle((i, 0), stripe_width, 80, linewidth=0, facecolor=color, alpha=0.8)
        ax.add_patch(stripe)

    # Draw pitch border
    pitch_border = patches.Rectangle((0, 0), 120, 80, linewidth=2, edgecolor='#007A6A', facecolor='none')
    ax.add_patch(pitch_border)

    # Add pitch markings
    ax.plot([60, 60], [0, 80], color='#007A6A', linestyle='-', linewidth=1, alpha=0.5)
    ax.plot(60, 40, 'o', color='#007A6A', markersize=8, alpha=0.5)
    circle = patches.Circle((60, 40), 9.15, fill=False, edgecolor='#007A6A', linewidth=1, alpha=0.5)
    ax.add_patch(circle)

    # Goal boxes
    ax.add_patch(patches.Rectangle((0, 18), 16, 44, linewidth=1, edgecolor='#007A6A', fill=False, alpha=0.5))
    ax.add_patch(patches.Rectangle((104, 18), 16, 44, linewidth=1, edgecolor='#007A6A', fill=False, alpha=0.5))

    # Plot locations by position with different colors
    total_touches = 0
    for position, locations in touches_by_position.items():
        if not locations:
            continue
        color = colors_map.get(position, '#808080')  # Gray default for unknown positions
        x_coords = [loc['x'] for loc in locations]
        y_coords = [loc['y'] for loc in locations]

        ax.scatter(x_coords, y_coords, c=color, s=200, alpha=0.6, edgecolors='none', zorder=5, label=position)
        total_touches += len(locations)

    # Set axis properties - clean visualization
    ax.set_xlim(-5, 125)
    ax.set_ylim(85, -5)  # Reversed: y=0 at bottom
    ax.set_aspect('equal')
    ax.axis('off')  # Remove all axis spines, ticks, and labels

    # Add legend
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=8)

    plt.tight_layout()
    plt.savefig(f'{title}.png', dpi=150, bbox_inches='tight')

    # Rotate image 90 degrees clockwise
    try:
        from PIL import Image
        img = Image.open(f'{title}.png')
        rotated_img = img.rotate(90, expand=True)
        rotated_img.save(f'{title}.png')
    except Exception as e:
        print(f"Warning: Could not rotate image: {e}")

    print(f"\n✓ Visualization saved to: {title}.png (rotated 90° clockwise)")
    print(f"Total touches visualized: {total_touches}")
    print(f"Positions included: {len(touches_by_position)}")
    plt.close(fig)

def visualize_shape(medians: dict, title: str = "Medians") -> None:
    """
    Visualize median x,y locations for all positions on a single plot.
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
    except ImportError:
        print("matplotlib required for visualization. Install with: pip install matplotlib")
        return

    # Color map for positions
    colors_map = {
        'Goalkeeper': '#000000',
        'Right Center Back': '#FF0000',
        'Left Center Back': '#FF6600',
        'Right Wing Back': '#FF0099',
        'Left Wing Back': '#00FF00',
        'Right Defensive Midfield': '#0099FF',
        'Left Defensive Midfield': '#9900FF',
        'Right Attacking Midfield': '#00FFFF',
        'Left Attacking Midfield': '#FFFF00',
    }

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(16, 12))

    # Draw football pitch with teal stripes for realistic look
    stripe_width = 10
    colors_stripes = ["#E6F4EA", "#C0DECD"]  # COLOR_TEAL_TINT, COLOR_TEAL_MID
    for i in range(0, 120, stripe_width):
        color = colors_stripes[(i // stripe_width) % 2]
        stripe = patches.Rectangle((i, 0), stripe_width, 80, linewidth=0, facecolor=color, alpha=0.8)
        ax.add_patch(stripe)

    # Draw pitch border
    pitch_border = patches.Rectangle((0, 0), 120, 80, linewidth=2, edgecolor='#007A6A', facecolor='none')
    ax.add_patch(pitch_border)

    # Add pitch markings
    ax.plot([60, 60], [0, 80], color='#007A6A', linestyle='-', linewidth=1, alpha=0.5)
    ax.plot(60, 40, 'o', color='#007A6A', markersize=8, alpha=0.5)
    circle = patches.Circle((60, 40), 9.15, fill=False, edgecolor='#007A6A', linewidth=1, alpha=0.5)
    ax.add_patch(circle)

    # Goal boxes
    ax.add_patch(patches.Rectangle((0, 18), 16, 44, linewidth=1, edgecolor='#007A6A', fill=False, alpha=0.5))
    ax.add_patch(patches.Rectangle((104, 18), 16, 44, linewidth=1, edgecolor='#007A6A', fill=False, alpha=0.5))

    # Scale circle size based on ball receipt counts
    counts = [m['count'] for m in medians.values()]
    min_count = min(counts)
    max_count = max(counts)
    min_size = 150  # 0.5x current size
    max_size = 600  # 2x current size

    # Plot median locations for each position
    for position, m in medians.items():
        color = colors_map.get(position, '#808080')  # Gray default

        # Calculate scaled size based on count
        if max_count == min_count:
            scaled_size = (min_size + max_size) / 2  # Use middle size if all counts are equal
        else:
            scaled_size = min_size + (m['count'] - min_count) / (max_count - min_count) * (max_size - min_size)

        ax.scatter(m['x'], m['y'], c=color, s=scaled_size, alpha=0.8, edgecolors='black', linewidth=2, zorder=5)

    # Set axis properties - clean visualization
    ax.set_xlim(-5, 125)
    ax.set_ylim(85, -5)  # Reversed: y=0 at bottom
    ax.set_aspect('equal')
    ax.axis('off')  # Remove all axis spines, ticks, and labels

    plt.tight_layout()
    plt.savefig(title + '.png', dpi=150, bbox_inches='tight')

    # Rotate image 90 degrees clockwise
    try:
        from PIL import Image
        img = Image.open('all_positions_median.png')
        rotated_img = img.rotate(90, expand=True)
        rotated_img.save('all_positions_median.png')
    except Exception as e:
        print(f"Warning: Could not rotate image: {e}")

    print(f"\n✓ Visualization saved to: all_positions_median.png (rotated 90° clockwise)")
    plt.close(fig)
