"""
Visualization utilities for football analytics.

Functions for plotting match events and statistics on a football pitch.
"""

from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from collections import deque

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
    plt.savefig('all_positions_median.png', dpi=150, bbox_inches='tight')

    # Rotate image 90 degrees clockwise
    try:
        from PIL import Image
        img = Image.open('all_positions_median.png')
        rotated_img = img.rotate(-90, expand=True)
        rotated_img.save('all_positions_median.png')
    except Exception as e:
        print(f"Warning: Could not rotate image: {e}")

    print(f"\n✓ Visualization saved to: all_positions_median.png (rotated 90° clockwise)")
    #plt.show()
