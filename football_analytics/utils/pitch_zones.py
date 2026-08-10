"""
StatsBomb pitch zones and lane definitions.

The StatsBomb pitch is 120 units (length) x 80 units (width),
with origin at bottom-left. X increases toward opponent goal,
Y increases toward right sideline.

This module defines pitch division thresholds and helper functions.
"""

# Pitch dimensions (StatsBomb standard)
PITCH_LENGTH = 120.0
PITCH_WIDTH = 80.0

# Vertical thirds (x-axis)
BUILDUP_X_THRESHOLD = 40.0      # Defensive third boundary
MIDDLE_X_START = 40.0           # Middle third starts
FINAL_X_START = 80.0            # Final third starts

# Horizontal lanes (y-axis)
WIDE_Y_MAX = 20.0               # Left wing upper bound
WIDE_Y_MIN = 60.0               # Right wing lower bound (inverted for symmetry)
LANE_LEFT_MAX = 20.0            # Left lane upper bound
LANE_RIGHT_MIN = 60.0           # Right lane lower bound

# Progression thresholds
PROGRESSIVE_PASS_THRESHOLD = 9.14  # ~10 yards, minimum forward progress


def get_zone(x: float) -> str:
    """
    Classify x-coordinate into defensive, middle, or final third.

    Tactical interpretation:
    - 'defensive': Building play, low-risk distribution
    - 'middle': Transition zone, balanced play
    - 'final': Attacking third, high-risk, high-reward

    Args:
        x: X-coordinate on pitch (0-120)

    Returns:
        'defensive', 'middle', or 'final'
    """
    if x < BUILDUP_X_THRESHOLD:
        return 'defensive'
    elif x < FINAL_X_START:
        return 'middle'
    else:
        return 'final'


def get_lane(y: float) -> str:
    """
    Classify y-coordinate into left, central, or right lane.

    Tactical interpretation:
    - 'left': Flank play, potential for crosses, 1v1 duels
    - 'central': Direct passing, central combination play
    - 'right': Flank play, wide attacks

    Args:
        y: Y-coordinate on pitch (0-80)

    Returns:
        'left', 'central', or 'right'
    """
    if y < LANE_LEFT_MAX:
        return 'left'
    elif y > LANE_RIGHT_MIN:
        return 'right'
    else:
        return 'central'


def is_progressive(start_x: float, end_x: float,
                   threshold: float = PROGRESSIVE_PASS_THRESHOLD) -> bool:
    """
    Determine if a pass is progressive (significant forward movement).

    Tactical interpretation:
    Progressive passes are those that advance the ball materially closer
    to the opponent goal, indicating attacking intent. Non-progressive
    passes (backward, lateral) indicate possession recycling.

    Args:
        start_x: Starting x-coordinate
        end_x: Ending x-coordinate
        threshold: Minimum x-distance to count as progressive (default 9.14m)

    Returns:
        True if end_x - start_x >= threshold
    """
    return (end_x - start_x) >= threshold


def is_wide(y: float) -> bool:
    """
    Determine if event is in wide channel.

    Args:
        y: Y-coordinate on pitch

    Returns:
        True if y < WIDE_Y_MAX or y > WIDE_Y_MIN
    """
    return y < WIDE_Y_MAX or y > WIDE_Y_MIN
