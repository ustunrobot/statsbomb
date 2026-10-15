#!/usr/bin/env python3
import math
from dataclasses import replace

"""Chart generation utilities for opposition reports."""

def reverse_metric_if_needed(metric):
    """
    Reverse metric values if metric.reverse is True (for "lower is better" metrics).

    For metrics where lower values are better (e.g., goals against, tackles needed),
    reverse the z_score and percentile_order so they display correctly in charts.

    Args:
        metric: Metric object to potentially reverse

    Returns:
        Metric object with reversed values if reverse=True, otherwise unchanged
    """
    if not metric.reverse:
        return metric

    # Reverse z_score: multiply by -1 to flip the direction
    reversed_z_score = -metric.z_score if metric.z_score != 0 else 0.0

    # Reverse percentile_order: rank 1/24 becomes 24/24
    reversed_percentile_order = metric.percentile_total + 1 - metric.percentile_order

    # Reverse secondary_z_score the same way as z_score, if present
    reversed_secondary_z_score = metric.secondary_z_score
    if reversed_secondary_z_score is not None:
        reversed_secondary_z_score = -reversed_secondary_z_score if reversed_secondary_z_score != 0 else 0.0

    # Return a new Metric with reversed values
    return replace(
        metric,
        z_score=reversed_z_score,
        percentile_order=reversed_percentile_order,
        secondary_z_score=reversed_secondary_z_score
    )


def create_pitch_background_for_thirds(width: int, height: int) -> str:
    """
    Create pitch background using professional pitch lines and circles.

    Based on section6 pitch design with proper proportions.
    """
    line_color = "#DADED9"

    # Standard football pitch: 100 yards wide x 68.5 yards tall
    px_per_yard_w = width / 100
    px_per_yard_h = height / 68.5

    # Calculate pitch elements
    center_circle_r = int(10 * px_per_yard_h)  # 10 yards radius
    penalty_width = int(22 * px_per_yard_w)  # 22 yards wide
    penalty_height = int(36 * px_per_yard_h)  # 36 yards deep
    goal_width = int(9 * px_per_yard_w)  # 9 yards wide
    goal_height = int(12 * px_per_yard_h)  # 12 yards deep

    center_y = height // 2
    penalty_y = int(center_y - penalty_height / 2)
    goal_y = int(center_y - goal_height / 2)

    svg = f"""        <!-- Halfway line -->
        <line x1="{width//2}" y1="0" x2="{width//2}" y2="{height}" stroke="{line_color}" stroke-width="1"/>

        <!-- Center circle -->
        <circle cx="{width//2}" cy="{center_y}" r="{center_circle_r}" fill="none" stroke="{line_color}" stroke-width="1"/>

        <!-- Center spot -->
        <circle cx="{width//2}" cy="{center_y}" r="2" fill="{line_color}"/>

        <!-- Left penalty area -->
        <rect x="0" y="{penalty_y}" width="{penalty_width}" height="{penalty_height}" fill="none" stroke="{line_color}" stroke-width="1"/>

        <!-- Right penalty area -->
        <rect x="{width - penalty_width}" y="{penalty_y}" width="{penalty_width}" height="{penalty_height}" fill="none" stroke="{line_color}" stroke-width="1"/>

        <!-- Left goal area -->
        <rect x="0" y="{goal_y}" width="{goal_width}" height="{goal_height}" fill="none" stroke="{line_color}" stroke-width="1"/>

        <!-- Right goal area -->
        <rect x="{width - goal_width}" y="{goal_y}" width="{goal_width}" height="{goal_height}" fill="none" stroke="{line_color}" stroke-width="1"/>
"""
    return svg

def create_heatmap_chart(heatmap_metric, optional_metric=None, high_resolution=True, reverse_metric=None, reverse_label=None, metric_label=None) -> str:
    """
    Create a heatmap visualization on a pitch showing cell values.

    If optional_metric is provided, display it on the left side like thirds chart,
    and show heatmap on the right side.

    If reverse_metric is provided, show side-by-side comparison with heatmap mirrored
    (both x and y values inverted) to show the opposite perspective.

    Colors cells based on values using a cold-to-warm spectrum:
    - Cold (blue): low values
    - Warm (red): high values

    Args:
        heatmap_metric: Metric object with populated heatmap field (20x30 grid for 4m x 4m cells)
        optional_metric: Optional metric to display on the left side
        high_resolution: If True, use 4m x 4m cells (20x30 grid). If False, use 8m x 8m cells (10x15 grid)
        reverse_metric: Optional metric to show with mirrored heatmap (x and y inverted)
        metric_label: Label for the original heatmap metric (used when reverse_metric is provided)
        reverse_label: Label for the reversed heatmap metric

    Returns:
        SVG string showing the heatmap on a pitch
    """
    if not heatmap_metric or not heatmap_metric.heatmap:
        return f"""    <svg width="320" height="240" viewBox="0 0 320 240" xmlns="http://www.w3.org/2000/svg" class="heatmap-chart">
        <rect width="320" height="240" fill="#f9f9f9"/>
        <text x="160" y="120" font-family="Inter, sans-serif" font-size="14" fill="#999" text-anchor="middle" dominant-baseline="middle">No heatmap data available</text>
    </svg>"""

    heatmap = heatmap_metric.heatmap

    # If low resolution, combine 2x2 cells to create 8m x 8m cells (10x15 grid)
    if not high_resolution:
        low_res_heatmap = []
        for row_idx in range(0, len(heatmap), 2):
            new_row = []
            for col_idx in range(0, len(heatmap[0]), 2):
                # Sum the 2x2 block
                cell_value = 0
                for dr in range(2):
                    for dc in range(2):
                        if row_idx + dr < len(heatmap) and col_idx + dc < len(heatmap[0]):
                            val = heatmap[row_idx + dr][col_idx + dc]
                            if val is not None:
                                cell_value += val
                new_row.append(cell_value)
            low_res_heatmap.append(new_row)
        heatmap = low_res_heatmap

    # Otherwise, create full-width heatmap
    width = 320
    height = 240

    # Grid dimensions based on original high-res grid: 20 rows x 30 columns (4m x 4m cells)
    cell_height = height / 20
    cell_width = width / 30

    # Find min and max values for normalization
    all_values = [val for row in heatmap for val in row if val is not None]
    if not all_values:
        max_val = 1.0
        min_val = 0.0
    else:
        max_val = max(all_values)
        min_val = min(all_values)

    # Avoid division by zero
    value_range = max_val - min_val
    if value_range == 0:
        value_range = 1.0

    def get_heatmap_color(value):
        """Get color from cold (blue) to warm (red) based on normalized value."""
        if value is None or value == 0:
            return "#f5f5f5"  # Very light gray for zero/empty

        # Normalize value to 0-1 range
        normalized = (value - min_val) / value_range

        # Create smooth color gradient from cold to warm
        # Cold (0): #1a4fa3 (blue)
        # Mid (0.5): #ffeb3b (yellow)
        # Warm (1): #ff5722 (red-orange)

        if normalized < 0.5:
            # Blue to Yellow: 0 to 0.5
            progress = normalized * 2  # 0 to 1
            r = int(26 + (255 - 26) * progress)  # 26 to 255
            g = int(79 + (235 - 79) * progress)  # 79 to 235
            b = int(163 - 163 * progress)  # 163 to 0
        else:
            # Yellow to Red: 0.5 to 1
            progress = (normalized - 0.5) * 2  # 0 to 1
            r = 255
            g = int(235 - (235 - 87) * progress)  # 235 to 87
            b = 59

        return f"#{r:02x}{g:02x}{b:02x}"

    # Build SVG
    svg = f"""    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" class="heatmap-chart">
        <!-- Pitch background -->
        <rect width="{width}" height="{height}" fill="#f9f9f9"/>

        <!-- Pitch markings from section6 -->
{create_pitch_background_for_thirds(width, height)}
"""

    # Add heatmap cells
    svg += "        <!-- Heatmap cells -->\n"
    for row_idx, row in enumerate(heatmap):
        for col_idx, value in enumerate(row):
            if value is not None and value > 0:
                # For low resolution, double the indices to get correct position in high-res grid
                display_row = row_idx * 2 if not high_resolution else row_idx
                display_col = col_idx * 2 if not high_resolution else col_idx

                x = display_col * cell_width
                y = display_row * cell_height

                # For low resolution, cells are 2x larger
                actual_cell_width = cell_width * (2 if not high_resolution else 1)
                actual_cell_height = cell_height * (2 if not high_resolution else 1)

                color = get_heatmap_color(value)

                # Cell with slight transparency to show pitch underneath
                svg += f'        <rect x="{x:.1f}" y="{y:.1f}" width="{actual_cell_width:.1f}" height="{actual_cell_height:.1f}" fill="{color}" opacity="0.7" stroke="none"/>\n'

    # Add color legend
    legend_y = height - 30
    legend_height = 12
    legend_width = 80

    # Legend background
    # svg += f'        <rect x="10" y="{legend_y - 5}" width="{legend_width + 20}" height="25" fill="white" opacity="0.8" stroke="#ddd" stroke-width="1"/>\n'

    # Cold to warm gradient legend
    for i in range(20):
        progress = i / 20
        test_value = min_val + (progress * value_range)
        color = get_heatmap_color(test_value)
        x = 160 + 15 + (i * legend_width / 20)
        svg += f'        <rect x="{x:.1f}" y="{legend_y}" width="{legend_width/20:.1f}" height="{legend_height}" fill="{color}" stroke="none"/>\n'

    # Legend labels
    svg += f'        <text x="175" y="{legend_y + legend_height + 10}" font-family="Inter, sans-serif" font-size="7" fill="#666">Low</text>\n'
    svg += f'        <text x="{160 +15 + legend_width - 15}" y="{legend_y + legend_height + 10}" font-family="Inter, sans-serif" font-size="7" fill="#666" text-anchor="end">High</text>\n'

    # Handle reverse_metric for side-by-side comparison with mirrored heatmap
    if reverse_metric and reverse_metric.heatmap:
        # Create mirrored heatmap (flip both x and y)
        mirrored_heatmap = reverse_metric.heatmap
        grid_rows = len(mirrored_heatmap)
        grid_cols = len(mirrored_heatmap[0]) if mirrored_heatmap else 30

        # Add labels for original and reversed metrics
        if metric_label:
            svg += f'        <text x="80" y="15" font-family="Inter, sans-serif" font-size="10" font-weight="600" fill="#999" text-anchor="middle">{metric_label}</text>\n'
        if reverse_label:
            svg += f'        <text x="240" y="15" font-family="Inter, sans-serif" font-size="10" font-weight="600" fill="#999" text-anchor="middle">{reverse_label}</text>\n'

        # Add original heatmap cells
        svg += "        <!-- Original heatmap cells -->\n"
        for row_idx, row in enumerate(heatmap):
            for col_idx, value in enumerate(row):
                if value is not None and value > 0:
                    display_row = row_idx * 2 if not high_resolution else row_idx
                    display_col = col_idx * 2 if not high_resolution else col_idx
                    x = display_col * cell_width
                    y = display_row * cell_height
                    actual_cell_width = cell_width * (2 if not high_resolution else 1)
                    actual_cell_height = cell_height * (2 if not high_resolution else 1)
                    color = get_heatmap_color(value)
                    svg += f'        <rect x="{x:.1f}" y="{y:.1f}" width="{actual_cell_width:.1f}" height="{actual_cell_height:.1f}" fill="{color}" opacity="0.7" stroke="none"/>\n'

        # Add mirrored heatmap cells (flip both row and column)
        svg += "        <!-- Mirrored heatmap cells -->\n"
        for row_idx, row in enumerate(mirrored_heatmap):
            for col_idx, value in enumerate(row):
                if value is not None and value > 0:
                    # Mirror both row and column: (row, col) -> (rows-1-row, cols-1-col)
                    mirrored_row = grid_rows - 1 - row_idx
                    mirrored_col = grid_cols - 1 - col_idx

                    display_row = mirrored_row * 2 if not high_resolution else mirrored_row
                    display_col = mirrored_col * 2 if not high_resolution else mirrored_col

                    x = display_col * cell_width
                    y = display_row * cell_height

                    actual_cell_width = cell_width * (2 if not high_resolution else 1)
                    actual_cell_height = cell_height * (2 if not high_resolution else 1)

                    color = get_heatmap_color(value)
                    svg += f'        <rect x="{x:.1f}" y="{y:.1f}" width="{actual_cell_width:.1f}" height="{actual_cell_height:.1f}" fill="{color}" opacity="0.7" stroke="none"/>\n'

    if optional_metric:
        # Add title and value on left half
        svg += f'        <text x="80" y="30" font-family="Inter, sans-serif" font-size="12" font-weight="600" fill="#999" text-anchor="middle">Final third</text>\n'
        svg += f'        <text x="80" y="55" font-family="Inter, sans-serif" font-size="12" font-weight="600" fill="#999" text-anchor="middle">long throw ratio</text>\n'
        svg += f'        <text x="240" y="30" font-family="Inter, sans-serif" font-size="12" font-weight="600" fill="#999" text-anchor="middle">Throw-in landings</text>\n'

        # Format and color the metric value
        if optional_metric.show_as_percentage and optional_metric.value_pg is not None:
            display_value = f"{optional_metric.value_pg * 100:.0f}%"
        else:
            display_value = f"{optional_metric.value_pg:.1f}" if optional_metric.value_pg is not None else f"{optional_metric.value:.1f}"

        # Color based on z-score
        clamped_z = max(-2.0, min(2.0, optional_metric.z_score))
        if clamped_z < -0.2:
            value_color = "#e74c3c"  # Red
        elif clamped_z > 0.2:
            value_color = "#239D56"  # Green
        else:
            value_color = "#666666"  # Dark gray

        svg += f'        <text x="80" y="95" font-family="Inter, sans-serif" font-size="20" font-weight="700" fill="{value_color}" text-anchor="middle">{display_value}</text>\n'

        # Add percentile below value
        percentile_text = f"P: {optional_metric.percentile_order}/{optional_metric.percentile_total}"
        svg += f'        <text x="80" y="130" font-family="Inter, sans-serif" font-size="10" fill="#666" text-anchor="middle">{percentile_text}</text>\n'

    svg += "    </svg>\n"
    return svg


def create_thirds_chart(defensive_metric, middle_metric, final_metric) -> str:
    """
    Create a pitch zones chart showing three metrics across defensive, middle, and final thirds.

    Each zone displays: metric name, value, percentile, and z-score bar.

    Args:
        defensive_metric: Metric object for defensive third
        middle_metric: Metric object for middle third
        final_metric: Metric object for final third

    Returns:
        SVG string showing the three metrics
    """
    width = 320
    height = 240
    zone_width = width / 3
    padding = 15
    inner_width = zone_width - 2 * padding

    # Color mapping by percentile rank (1 = best), same thresholds as
    # render_metric_cards()/create_radar_chart(): bottom quartile-ish
    # (rank >= 18/24) is red, top quintile-ish (rank <= 5/24) is green,
    # everything else is neutral gray.
    def get_color(metric):
        if metric.percentile_total:
            rank_fraction = metric.percentile_order / metric.percentile_total
        else:
            rank_fraction = 0.5

        if rank_fraction >= 18 / 24:
            return "#e74c3c"  # Red
        elif rank_fraction <= 5 / 24:
            return "#239D56"  # Green
        else:
            return "#666666"  # Dark gray

    # Z-score bar position mapping (-2 to +2 -> 0 to inner_width)
    def zscore_to_x(z_score):
        clamped_z = max(-2.0, min(2.0, z_score))
        return padding + ((clamped_z + 2) / 4) * inner_width

    def render_zone(metric, zone_name, x_offset):
        """Render a single zone with metric data."""
        svg = f'    <!-- {zone_name} Zone -->\n'
        svg += f'    <g transform="translate({x_offset}, 0)">\n'

        # Zone background (transparent to show pitch lines)
        svg += f'        <rect width="{zone_width}" height="{height}" fill="transparent" stroke="none"/>\n'

        # Metric value (big font)
        if metric.show_as_percentage and metric.value_pg is not None:
            display_value = f"{metric.value_pg * 100:.0f}%"
        else:
            display_value = f"{metric.value_pg:.1f}" if metric.value_pg is not None else f"{metric.value:.1f}"

        value_color = get_color(metric)
        svg += f'        <text x="{zone_width/2}" y="70" font-family="Inter, sans-serif" font-size="24" font-weight="700" fill="{value_color}" text-anchor="middle">{display_value}</text>\n'

        # Percentile info (moved right, larger font)
        percentile_text = f"P: {metric.percentile_order}/{metric.percentile_total}"
        svg += f'        <text x="{zone_width - padding - 5}" y="110" font-family="Inter, sans-serif" font-size="10" fill="#999" text-anchor="end">{percentile_text}</text>\n'

        # Z-score bar background (scale from -2 to +2, positioned right)
        bar_y = 200
        bar_height = 12
        bar_width = inner_width * 0.7  # 70% of inner width
        bar_x = zone_width - padding - bar_width
        svg += f'        <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" fill="#f0f0f0" stroke="#d9d9d9" stroke-width="1"/>\n'

        # Center line (0 z-score)
        center_x = bar_x + (bar_width / 2)
        svg += f'        <line x1="{center_x}" y1="{bar_y}" x2="{center_x}" y2="{bar_y + bar_height}" stroke="#bfbfbf" stroke-width="1" stroke-dasharray="2,2"/>\n'

        # Z-score indicator bar (mapped to the right-aligned bar)
        clamped_z = max(-2.0, min(2.0, metric.z_score))
        bar_value_x = bar_x + ((clamped_z + 2) / 4) * bar_width
        bar_color = get_color(metric)

        # Draw filled rect from center to value position
        if metric.z_score >= 0:
            bar_left = center_x
            bar_actual_width = bar_value_x - center_x
        else:
            bar_left = bar_value_x
            bar_actual_width = center_x - bar_value_x

        if bar_actual_width > 0:
            svg += f'        <rect x="{bar_left}" y="{bar_y}" width="{bar_actual_width}" height="{bar_height}" fill="{bar_color}" opacity="0.7"/>\n'

        # Z-score value indicator
        svg += f'        <circle cx="{bar_value_x}" cy="{bar_y + bar_height/2}" r="2.5" fill="{bar_color}"/>\n'

        # Z-score scale labels
        svg += f'        <text x="{bar_x}" y="{bar_y + bar_height + 12}" font-family="Inter, sans-serif" font-size="7" fill="#999">-2</text>\n'
        svg += f'        <text x="{center_x - 3}" y="{bar_y + bar_height + 12}" font-family="Inter, sans-serif" font-size="7" fill="#999" text-anchor="middle">0</text>\n'
        svg += f'        <text x="{bar_x + bar_width}" y="{bar_y + bar_height + 12}" font-family="Inter, sans-serif" font-size="7" fill="#999" text-anchor="end">+2</text>\n'

        svg += f'    </g>\n'
        return svg

    # Build main SVG
    svg = f"""    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" class="thirds-chart">
        <!-- Pitch background -->
        <rect width="{width}" height="{height}" fill="#f0fdf4"/>

        <!-- Pitch markings from section6 -->
{create_pitch_background_for_thirds(width, height)}
"""

    # Render each zone
    svg += render_zone(defensive_metric, "Defensive", 0)
    svg += render_zone(middle_metric, "Middle", zone_width)
    svg += render_zone(final_metric, "Final", zone_width * 2)

    # Add attack direction arrow at the bottom
    arrow_y = 20
    arrow_start_x = 80
    arrow_end_x = width - 80
    arrow_head_size = 6

    # Arrow line
    svg += f'        <line x1="{arrow_start_x}" y1="{arrow_y}" x2="{arrow_end_x}" y2="{arrow_y}" stroke="#BBB" stroke-width="2"/>\n'

    # Arrow head (triangle pointing right)
    svg += f'        <polygon points="{arrow_end_x},{arrow_y} {arrow_end_x - arrow_head_size},{arrow_y - arrow_head_size} {arrow_end_x - arrow_head_size},{arrow_y + arrow_head_size}" fill="#BBB"/>\n'

    # Attack direction label
    svg += f'        <text x="{width/2}" y="{arrow_y + 15}" font-family="Inter, sans-serif" font-size="8" fill="#BBB" text-anchor="middle">Attack Direction</text>\n'

    svg += "    </svg>\n"
    return svg


def create_radar_chart(metrics: dict, default_size: int = 320) -> str:
    """Create an SVG radar chart for metrics."""    
    metric_names = list(metrics.keys())
    metric_count = len(metric_names)

    # Chart dimensions (reduced to fit 2 squares side-by-side)
    size = default_size  # Reduced from 360 to fit two squares
    center_x = size / 2
    center_y = size / 2
    max_radius = (size / 2 - 30) * 0.7  # 30% smaller radar for space for labels

    # Convert z-score to radius value (clamped -2 to +2 becomes 0-max_radius)
    def zscore_to_radius(z_score):
        clamped_z = max(-2.0, min(2.0, z_score))
        # Map -2 to +2 range to 0 to max_radius
        return ((clamped_z + 2) / 4) * max_radius

    # Calculate angle for each metric (starting from top, going clockwise)
    def calculate_point(metric_index, radius):
        angle = (metric_index / metric_count) * 2 * math.pi - math.pi / 2
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        return x, y

    # Build SVG
    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" class="radar-chart">
        <!-- Background with border -->
        <rect width="{size}" height="{size}" fill="white" stroke="#d9d9d9" stroke-width="1"/>

        <!-- Grid circles and levels -->
    """

    # Draw concentric circles and level labels (z-score scale: -2, -1, 0, +1, +2)
    z_scores = [-2, -1, 0, 1, 2]
    for z in z_scores:
        radius = zscore_to_radius(z)
        if z == 0:
            # Highlight the average line
            svg += f'        <circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="none" stroke="#bfbfbf" stroke-width="1.5" stroke-dasharray="3,3"/>\n'
            svg += f'        <text x="{center_x + 8}" y="{center_y - radius + 5}" font-family="Inter, sans-serif" font-size="8" fill="#666" font-weight="600">0</text>\n'
        else:
            svg += f'        <circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="none" stroke="#e5e5e5" stroke-width="1"/>\n'
            label = f"{z:+d}" if z != 0 else "0"
            svg += f'        <text x="{center_x + 8}" y="{center_y - radius + 5}" font-family="Inter, sans-serif" font-size="8" fill="#999">{label}</text>\n'

    # Draw radial lines
    for i in range(metric_count):
        x, y = calculate_point(i, max_radius)
        svg += f'        <line x1="{center_x}" y1="{center_y}" x2="{x}" y2="{y}" stroke="#e5e5e5" stroke-width="1"/>\n'

    # Collect points for the secondary (comparison) polygon, using secondary_z_score
    # where available - falling back to the same z_score otherwise - and draw it
    # first so the primary polygon renders on top of it.
    secondary_points = []
    for i, (metric_name, metric) in enumerate(metrics.items()):
        metric = reverse_metric_if_needed(metric)
        secondary_z = metric.secondary_z_score if metric.secondary_z_score is not None else metric.z_score
        radius = zscore_to_radius(secondary_z)
        x, y = calculate_point(i, radius)
        secondary_points.append(f"{x},{y}")

    secondary_points_str = " ".join(secondary_points)
    svg += f'        <polygon points="{secondary_points_str}" fill="#999999" fill-opacity="0.2" stroke="#8e44ad" stroke-width="1.5" stroke-dasharray="4,2"/>\n'

    # Collect points for the polygon
    points = []
    for i, (metric_name, metric) in enumerate(metrics.items()):
        metric = reverse_metric_if_needed(metric)
        radius = zscore_to_radius(metric.z_score)
        x, y = calculate_point(i, radius)
        points.append(f"{x},{y}")

    # Draw filled polygon
    points_str = " ".join(points)
    svg += f'        <polygon points="{points_str}" fill="#1a4fa3" fill-opacity="0.3" stroke="#1a4fa3" stroke-width="2"/>\n'

    # Draw data points
    for i, (metric_name, metric) in enumerate(metrics.items()):
        metric = reverse_metric_if_needed(metric)
        radius = zscore_to_radius(metric.z_score)
        x, y = calculate_point(i, radius)
        svg += f'        <circle cx="{x}" cy="{y}" r="4" fill="#1a4fa3" stroke="white" stroke-width="1.5"/>\n'

    # Draw metric labels and values
    for i, (metric_name, metric) in enumerate(metrics.items()):
        metric = reverse_metric_if_needed(metric)
        # Determine color by percentile rank (1 = best after reversal above), same
        # thresholds as render_metric_cards(): bottom quartile-ish (rank >= 18/24)
        # is red, top quintile-ish (rank <= 5/24) is green, else neutral gray.
        if metric.percentile_total:
            rank_fraction = metric.percentile_order / metric.percentile_total
        else:
            rank_fraction = 0.5

        if rank_fraction >= 18 / 24:
            value_color = "#e74c3c"  # Red
        elif rank_fraction <= 5 / 24:
            value_color = "#27ae60"  # Green
        else:
            value_color = "#666666"  # Dark gray

        label_radius = max_radius + 25
        x, y = calculate_point(i, label_radius)

        # Use label2 if available, otherwise use label
        display_label = metric.label2 if metric.label2 else metric.label

        # Metric name
        svg += f'        <text x="{x}" y="{y}" font-family="Inter, sans-serif" font-size="10" font-weight="400" fill="#777777" text-anchor="middle" dominant-baseline="middle">{display_label}</text>\n'

        # Metric value and percentile order (same line, different colors)
        if metric.show_as_percentage and metric.value_pg is not None:
            display_value = f"{metric.value_pg * 100:.0f}%"
        else:
            display_value = f"{metric.value_pg:.1f}" if metric.value_pg is not None else f"{metric.value:.1f}"
        percentile_text = f"P: {metric.percentile_order}/{metric.percentile_total}"
        svg += f'        <text x="{x}" y="{y + 12}" font-family="Inter, sans-serif" font-size="9" font-weight="600" text-anchor="middle" dominant-baseline="middle"><tspan fill="{value_color}">{display_value}</tspan> <tspan fill="#1a4fa3">{percentile_text}</tspan></text>\n'

    svg += "    </svg>\n"
    return svg


def create_scatter_chart(all_metrics: dict, all_teams_statsbomb_metrics: dict, team_name: str,
                        x_metric_key: str = 'xg_for_total', y_metric_key: str = 'xg_against_total',
                        x_axis_label: str = 'xGF', y_axis_label: str = 'xGA',
                        quadrants: dict = None, league_table: dict = None) -> str:
    """Create an SVG scatter chart for two metrics as x and y axes.

    Args:
        all_metrics: Team metrics organized by team_id (from event data)
        all_teams_statsbomb_metrics: StatsBomb metrics for all teams organized by team_name
        team_name: Name of the main team to highlight
        x_metric_key: Metric key for x-axis (default: 'xg_for_total')
        y_metric_key: Metric key for y-axis (default: 'xg_against_total')
        x_axis_label: Label for x-axis (default: 'xGF')
        y_axis_label: Label for y-axis (default: 'xGA')
        quadrants: Dict with quadrant labels {
            'top_right': 'High Risk',
            'bottom_right': 'Dominant',
            'top_left': 'Under Pressure',
            'bottom_left': 'Compact'
        }
        league_table: Optional league table dict with team rankings
    """
    if quadrants is None:
        quadrants = {
            'top_right': 'High Risk',
            'bottom_right': 'Dominant',
            'top_left': 'Under Pressure',
            'bottom_left': 'Compact'
        }

    main_team_data = None

    # Build teams_comparison list from all_metrics for scatter chart
    # all_metrics is organized by team_id directly
    teams_comparison = []

    # Iterate through all teams directly
    for team_id, team_data in all_metrics.items():
        if isinstance(team_data, dict):
            # Try to get x_metric from all_metrics, then fallback to all_teams_statsbomb_metrics
            x_metric = team_data.get(x_metric_key)
            current_team_name = team_data.get('team_name', f'Team {team_id}')
            if not x_metric and current_team_name in all_teams_statsbomb_metrics:
                x_metric = all_teams_statsbomb_metrics[current_team_name].get(x_metric_key)

            # Try to get y_metric from all_metrics, then fallback to all_teams_statsbomb_metrics
            y_metric = team_data.get(y_metric_key)
            if not y_metric and current_team_name in all_teams_statsbomb_metrics:
                y_metric = all_teams_statsbomb_metrics[current_team_name].get(y_metric_key)

            if x_metric and y_metric:
                x_z_orig = x_metric.z_score
                y_z_orig = y_metric.z_score

                # Clamp z-scores to [-2, 2] range for chart display
                x_z = max(-2.0, min(2.0, x_z_orig))
                y_z = max(-2.0, min(2.0, y_z_orig))

                team_entry = {
                    'name': current_team_name,
                    'x_z': x_z,
                    'y_z': y_z
                }
                teams_comparison.append(team_entry)

                # Identify main team
                if current_team_name == team_name:
                    main_team_data = team_entry

    # Extract main team z-scores, with fallback for missing metrics
    if main_team_data:
        x_z = main_team_data['x_z']
        y_z = main_team_data['y_z']
    else:
        # Last resort: try to get from all_teams_statsbomb_metrics directly
        team_metrics_fallback = all_teams_statsbomb_metrics.get(team_name, {})
        x_metric = team_metrics_fallback.get(x_metric_key)
        y_metric = team_metrics_fallback.get(y_metric_key)
        x_z = x_metric.z_score if x_metric else 0.0
        y_z = y_metric.z_score if y_metric else 0.0

    # Chart dimensions
    size = 320
    margin = 40
    chart_width = size - 2 * margin
    chart_height = size - 2 * margin
    origin_x = margin
    origin_y = size - margin

    # Map z-score (-2 to +2) to pixel position
    def z_score_to_x(z_score):
        return origin_x + ((z_score + 2) / 4) * chart_width

    def z_score_to_y(z_score):
        return origin_y - ((z_score + 2) / 4) * chart_height

    # Build SVG
    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" class="scatter-chart">
        <!-- Background with border -->
        <rect width="{size}" height="{size}" fill="white" stroke="#d9d9d9" stroke-width="1"/>

        <!-- Axes (3 shades darker) -->
        <line x1="{origin_x}" y1="{origin_y}" x2="{size - margin}" y2="{origin_y}" stroke="#808080" stroke-width="1"/>
        <line x1="{origin_x}" y1="{margin}" x2="{origin_x}" y2="{origin_y}" stroke="#808080" stroke-width="1"/>

        <!-- Grid lines at 0 (center, 2 shades darker) -->
        <line x1="{z_score_to_x(0)}" y1="{margin}" x2="{z_score_to_x(0)}" y2="{origin_y}" stroke="#bfbfbf" stroke-width="1" stroke-dasharray="2,2"/>
        <line x1="{origin_x}" y1="{z_score_to_y(0)}" x2="{size - margin}" y2="{z_score_to_y(0)}" stroke="#bfbfbf" stroke-width="1" stroke-dasharray="2,2"/>

        <!-- Axis labels (3 shades darker) -->
        <text x="{size - margin - 25}" y="{origin_y + 24}" font-family="Inter, sans-serif" font-size="9" fill="#555555">{x_axis_label}</text>
        <text x="{origin_x - 20}" y="{margin - 5}" font-family="Inter, sans-serif" font-size="9" fill="#555555">{y_axis_label}</text>

        <!-- Scale labels (3 shades darker) -->
        <text x="{origin_x - 3}" y="{origin_y + 12}" font-family="Inter, sans-serif" font-size="8" fill="#808080" text-anchor="end">-2</text>
        <text x="{z_score_to_x(0) + 1}" y="{origin_y + 12}" font-family="Inter, sans-serif" font-size="8" fill="#808080" text-anchor="middle">0</text>
        <text x="{size - margin + 1}" y="{origin_y + 12}" font-family="Inter, sans-serif" font-size="8" fill="#808080" text-anchor="start">+2</text>

        <text x="{origin_x - 5}" y="{margin + 2}" font-family="Inter, sans-serif" font-size="8" fill="#808080" text-anchor="end">+2</text>
        <text x="{origin_x - 5}" y="{z_score_to_y(0) + 2}" font-family="Inter, sans-serif" font-size="8" fill="#808080" text-anchor="end">0</text>
        <text x="{origin_x - 5}" y="{origin_y + 2}" font-family="Inter, sans-serif" font-size="8" fill="#808080" text-anchor="end">-2</text>
    """

    # Extract Crawley Town data if it exists and is not the main team
    crawley_town_data = None
    if team_name != "Crawley Town":
        for team in teams_comparison:
            if team["name"] == "Crawley Town":
                crawley_town_data = team
                break

    # Draw comparison teams (context) with rankings
    for team in teams_comparison:
        # Skip the main team - it will be drawn separately with special styling
        if team["name"] == team_name:
            continue

        # Skip Crawley Town if we're showing it separately (as benchmark)
        if crawley_town_data and team["name"] == "Crawley Town":
            continue

        x = z_score_to_x(team["x_z"])
        y = z_score_to_y(team["y_z"])

        # Get team ranking from league table if available
        rank = None
        if league_table and team["name"] in league_table:
            rank = league_table[team["name"]].get('rank', '?')

        # Determine circle color and size for comparison teams
        circle_color = "#D2C74D"
        circle_radius = 6
        text_color = "#514F4F"

        # Draw circle
        svg += f'        <circle cx="{x}" cy="{y}" r="{circle_radius}" fill="{circle_color}" opacity="0.8"/>\n'

        # Add rank number inside circle
        if rank:
            svg += f'        <text x="{x}" y="{y}" font-family="Inter, sans-serif" font-size="8" font-weight="700" fill="{text_color}" text-anchor="middle" dominant-baseline="middle">{rank}</text>\n'

    # Draw Crawley Town as benchmark (blue circle) if selected team is not Crawley Town
    if crawley_town_data:
        x = z_score_to_x(crawley_town_data["x_z"])
        y = z_score_to_y(crawley_town_data["y_z"])

        # Get Crawley Town ranking
        crawley_rank = None
        if league_table and "Crawley Town" in league_table:
            crawley_rank = league_table["Crawley Town"].get('rank', '?')

        # Draw Crawley Town with blue styling
        svg += f'        <circle cx="{x}" cy="{y}" r="6" fill="none" stroke="#1a4fa3" stroke-width="2"/>\n'

        # Add rank number inside circle if available
        if crawley_rank:
            svg += f'        <text x="{x}" y="{y}" font-family="Inter, sans-serif" font-size="8" font-weight="700" fill="#1a4fa3" text-anchor="middle" dominant-baseline="middle">{crawley_rank}</text>\n'

        # Add Crawley Town label
        svg += f'        <text x="{x + 10}" y="{y - 8}" font-family="Inter, sans-serif" font-size="8" font-weight="600" fill="#1a4fa3">Crawley Town</text>\n'

    # Draw main team from all_metrics (using actual z-scores)
    x = z_score_to_x(x_z)
    y = z_score_to_y(y_z)

    # Get main team ranking
    main_rank = None
    if league_table and team_name in league_table:
        main_rank = league_table[team_name].get('rank', '?')

    svg += f'        <circle cx="{x}" cy="{y}" r="8" fill="#E11111" stroke="#ffffff" stroke-width="2"/>\n'

    # Add rank number in circle for main team
    if main_rank:
        svg += f'        <text x="{x}" y="{y}" font-family="Inter, sans-serif" font-size="10" font-weight="700" fill="#ffffff" text-anchor="middle" dominant-baseline="middle">{main_rank}</text>\n'

    # Add main team label
    svg += f'        <text x="{x + 12}" y="{y - 10}" font-family="Inter, sans-serif" font-size="9" font-weight="600" fill="#E11111">{team_name}</text>\n'

    # Add quadrant labels with football terminology
    # Top-right
    svg += f'        <text x="{size - margin - 20}" y="{margin + 15}" font-family="Inter, sans-serif" font-size="9" fill="#666" text-anchor="end" font-weight="500">{quadrants["top_right"]}</text>\n'

    # Bottom-right
    svg += f'        <text x="{size - margin - 20}" y="{origin_y - 10}" font-family="Inter, sans-serif" font-size="9" fill="#27ae60" text-anchor="end" font-weight="500">{quadrants["bottom_right"]}</text>\n'

    # Top-left
    svg += f'        <text x="{origin_x + 20}" y="{margin + 15}" font-family="Inter, sans-serif" font-size="9" fill="#e74c3c" text-anchor="start" font-weight="500">{quadrants["top_left"]}</text>\n'

    # Bottom-left
    svg += f'        <text x="{origin_x + 20}" y="{origin_y - 10}" font-family="Inter, sans-serif" font-size="9" fill="#f39c12" text-anchor="start" font-weight="500">{quadrants["bottom_left"]}</text>\n'

    svg += "    </svg>\n"
    return svg


def create_discipline_score_chart(discipline_metric) -> str:
    """
    Create a discipline score visualization with z-score bar and percentile.

    Args:
        discipline_metric: Metric object with discipline_score data

    Returns:
        SVG string showing discipline score bar chart
    """
    if not discipline_metric or discipline_metric.value is None:
        return """    <svg width="280" height="144" viewBox="0 0 280 144" xmlns="http://www.w3.org/2000/svg" class="discipline-chart">
        <rect width="280" height="144" fill="#f9f9f9"/>
        <text x="140" y="72" font-family="Inter, sans-serif" font-size="12" fill="#999" text-anchor="middle" dominant-baseline="middle">No data</text>
    </svg>"""

    discipline_metric.reverse = True  # Reverse the metric for visualization (lower is better)
    discipline_metric = reverse_metric_if_needed(discipline_metric)
    score = discipline_metric.value
    z_score = discipline_metric.z_score if hasattr(discipline_metric, 'z_score') else 0
    percentile = discipline_metric.percentile_order if hasattr(discipline_metric, 'percentile_order') else 0
    percentile_total = discipline_metric.percentile_total if hasattr(discipline_metric, 'percentile_total') else 24

    # Clamp z-score to -2 to 2 for visualization
    clamped_z = max(-2.0, min(2.0, z_score))
    bar_width = 200
    bar_height = 24
    center_x = 140
    bar_y = 40

    # Determine color based on discipline (lower is worse, higher is better)
    if clamped_z < -0.5:
        color = "#f33c09"  # Green (good discipline)
    elif clamped_z > 0.5:
        color = "#3fbf22"  # Red (poor discipline)
    else:
        color = "#f39c12"  # Orange (average)

    # Calculate bar position
    # -2 to +2 range: -2 is 0px, 0 is 100px, +2 is 200px
    bar_pos = (clamped_z + 2.0) / 4.0 * bar_width

    svg = f"""    <svg width="280" height="144" viewBox="0 0 280 144" xmlns="http://www.w3.org/2000/svg" class="discipline-chart">
        <rect width="280" height="144" fill="#f9f9f9" rx="6"/>

        <!-- Title -->
        <text x="140" y="20" font-family="Inter, sans-serif" font-size="13" font-weight="600" fill="#333" text-anchor="middle">Discipline</text>

        <!-- Score value -->
        <text x="140" y="40" font-family="Inter, sans-serif" font-size="18" font-weight="700" fill="{color}" text-anchor="middle">{score:.0f}</text>

        <!-- Scale background -->
        <rect x="40" y="55" width="{bar_width}" height="{bar_height}" fill="#e8e8e8" rx="3"/>

        <!-- Scale gradient stops (visual guide) --> 
        <rect x="40" y="55" width="{bar_width * 0.33}" height="{bar_height}" fill="#e74c3c11" rx="3"/>
        <rect x="{40 + bar_width * 0.67}" y="55" width="{bar_width * 0.33}" height="{bar_height}" fill="#27ae6011" rx="3"/>

        <!-- Indicator bar -->
        <rect x="{40 + bar_pos - 3}" y="51" width="6" height="{bar_height + 8}" fill="{color}" rx="2"/>

        <!-- Scale labels -->
        <text x="40" y="95" font-family="Inter, sans-serif" font-size="9" fill="#999">Reckless</text>
        <text x="{40 + bar_width - 20}" y="95" font-family="Inter, sans-serif" font-size="9" fill="#999" text-anchor="end">Composed</text>

        <!-- Z-score info -->
        <text x="140" y="120" font-family="Inter, sans-serif" font-size="10" fill="#666" text-anchor="middle">Z: {z_score:.1f}</text>

        <!-- Percentile info -->
        <text x="140" y="135" font-family="Inter, sans-serif" font-size="10" fill="#666" text-anchor="middle">Rank: {percentile}/{percentile_total}</text>
    </svg>"""

    return svg


def create_card_counter_chart(yellow_cards, red_cards) -> str:
    """
    Create a card counter visualization showing yellow and red cards as rectangles.

    Args:
        yellow_cards: Metric object with yellow_card data
        red_cards: Metric object with red_card data

    Returns:
        SVG string showing card counters as referee-style cards
    """
    yellow_value = int(yellow_cards.value) if yellow_cards and yellow_cards.value else 0
    yellow_avg = round(yellow_cards.average, 2) if yellow_cards and yellow_cards.average else 0

    red_value = int(red_cards.value) if red_cards and red_cards.value else 0
    red_avg = round(red_cards.average, 2) if red_cards and red_cards.average else 0

    svg = f"""    <svg width="280" height="144" viewBox="0 0 280 144" xmlns="http://www.w3.org/2000/svg" class="card-counter-chart">
        <rect width="280" height="144" fill="#f9f9f9" rx="6"/>

        <!-- Title -->
        <text x="140" y="20" font-family="Inter, sans-serif" font-size="13" font-weight="600" fill="#333" text-anchor="middle">Cards</text>

        <!-- Yellow Card (Rectangle like referee card) -->
        <rect x="55" y="35" width="32" height="50" fill="#ffeb3b" stroke="#f39c12" stroke-width="2" rx="2"/>
        <text x="71" y="68" font-family="Inter, sans-serif" font-size="22" font-weight="700" fill="#f39c12" text-anchor="middle" dominant-baseline="middle">{yellow_value}</text>

        <text x="71" y="105" font-family="Inter, sans-serif" font-size="11" font-weight="600" fill="#333" text-anchor="middle">Yellow</text>
        <text x="71" y="120" font-family="Inter, sans-serif" font-size="9" fill="#999" text-anchor="middle">{yellow_avg}/m</text>

        <!-- Red Card (Rectangle like referee card) -->
        <rect x="193" y="35" width="32" height="50" fill="#ff5722" stroke="#c62828" stroke-width="2" rx="2"/>
        <text x="209" y="68" font-family="Inter, sans-serif" font-size="22" font-weight="700" fill="white" text-anchor="middle" dominant-baseline="middle">{red_value}</text>

        <text x="209" y="105" font-family="Inter, sans-serif" font-size="11" font-weight="600" fill="#333" text-anchor="middle">Red</text>
        <text x="209" y="120" font-family="Inter, sans-serif" font-size="9" fill="#999" text-anchor="middle">{red_avg}/m</text>
    </svg>"""

    return svg


def create_trend_chart(series_data: dict, title: str = "Performance Trend") -> str:
    """
    Create a trend line chart showing multiple series over 4 periods.

    Each series is normalized using z-score for better cross-series comparison.

    Args:
        series_data: Dict with series names as keys and lists of 4 values as values
                    {
                        "Series 1": [past_val, last_2_val, last_1_val, last_val],
                        "Series 2": [...],
                        "Series 3": [...]
                    }
        title: Chart title

    Returns:
        SVG string showing trend lines with z-score normalization
    """
    import math

    width = 320
    height = 200
    margin_left = 40
    margin_right = 15
    margin_top = 30
    margin_bottom = 35

    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom

    # Period labels
    periods = ["Past Games Avg", "Last-2", "Last-1", "Last Game"]

    # Colors for 3 series
    colors = ["#1a4fa3", "#e74c3c", "#27ae60"]  # Blue, Red, Green

    # Normalize each series using z-score
    normalized_series = {}
    for series_name, values in series_data.items():
        valid_values = [v for v in values if v is not None]
        if not valid_values:
            continue

        # Calculate mean and standard deviation
        mean = sum(valid_values) / len(valid_values)
        variance = sum((v - mean) ** 2 for v in valid_values) / len(valid_values)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0

        # Calculate z-scores and clamp to [-2, 2] range
        z_scores = []
        for v in values:
            if v is None:
                z_scores.append(None)
            else:
                z_score = (v - mean) / std_dev
                # Clamp to [-2, 2] range
                z_score = max(-2.0, min(2.0, z_score))
                z_scores.append(z_score)

        normalized_series[series_name] = z_scores

    if not normalized_series:
        return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{width}" height="{height}" fill="#f9f9f9" rx="4"/>
            <text x="{width/2}" y="{height/2}" font-family="Inter, sans-serif" font-size="12" fill="#999" text-anchor="middle" dominant-baseline="middle">No trend data</text>
        </svg>"""

    # Fixed z-score range: -2 to +2
    z_min = -2.0
    z_max = 2.0

    def value_to_y(z_score):
        """Convert z-score to y coordinate (fixed -2 to +2 range)."""
        if z_score is None:
            return None
        # Map z-score to pixel coordinate with 0 at center
        normalized = (z_score - z_min) / (z_max - z_min)  # Normalize to 0-1
        return margin_top + chart_height - (normalized * chart_height)

    def period_to_x(period_idx):
        """Convert period index to x coordinate."""
        return margin_left + (period_idx / 3) * chart_width

    # Build SVG
    svg = f"""    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" class="trend-chart">
        <rect width="{width}" height="{height}" fill="#f9f9f9" rx="6"/>

        <!-- Title -->
        <text x="{width/2}" y="25" font-family="Inter, sans-serif" font-size="14" font-weight="600" fill="#999" text-anchor="middle">{title}</text>

        <!-- Y-axis background grid -->
        <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" stroke="#333" stroke-width="1"/>

        <!-- X-axis -->
        <line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{width - margin_right}" y2="{margin_top + chart_height}" stroke="#333" stroke-width="1"/>

        <!-- Grid lines and labels -->
"""

    # Add horizontal grid lines for z-score range (-2, -1, 0, 1, 2)
    for z in [-2.0, -1.0, 0.0, 1.0, 2.0]:
        y = value_to_y(z)
        if y is not None:
            if z == 0.0:
                # Center line (z=0) - stronger
                svg += f'        <line x1="{margin_left}" y1="{y}" x2="{width - margin_right}" y2="{y}" stroke="#999" stroke-width="1" stroke-dasharray="3,3"/>\n'
                svg += f'        <text x="{margin_left - 5}" y="{y + 3}" font-family="Inter, sans-serif" font-size="8" fill="#999" text-anchor="end">0</text>\n'
            else:
                # Grid lines
                svg += f'        <line x1="{margin_left}" y1="{y}" x2="{width - margin_right}" y2="{y}" stroke="#c5c5c5" stroke-width="0.7" stroke-dasharray="2,2"/>\n'
                svg += f'        <text x="{margin_left - 5}" y="{y + 3}" font-family="Inter, sans-serif" font-size="7" fill="#ccc" text-anchor="end">{z:+.0f}</text>\n'

    # Period labels
    for i, period in enumerate(periods):
        x = period_to_x(i)
        svg += f'        <text x="{x}" y="{margin_top + chart_height + 15}" font-family="Inter, sans-serif" font-size="9" fill="#666" text-anchor="middle">{period}</text>\n'

    # Draw series
    for series_idx, (series_name, normalized_values) in enumerate(normalized_series.items()):
        color = colors[series_idx % len(colors)]

        # Build path
        points = []
        for period_idx, normalized_val in enumerate(normalized_values):
            if normalized_val is not None:
                x = period_to_x(period_idx)
                y = value_to_y(normalized_val)
                points.append((x, y))

        # Draw line
        if len(points) > 1:
            path_d = f"M {points[0][0]} {points[0][1]}"
            for x, y in points[1:]:
                path_d += f" L {x} {y}"
            svg += f'        <path d="{path_d}" stroke="{color}" stroke-width="2" fill="none"/>\n'

        # Draw points
        for x, y in points:
            svg += f'        <circle cx="{x}" cy="{y}" r="2.5" fill="{color}" stroke="white" stroke-width="0.5"/>\n'

        # Add legend
        legend_x = width - margin_right - 80
        legend_y = margin_top + (series_idx * 14)
        svg += f'        <circle cx="{legend_x}" cy="{legend_y}" r="2" fill="{color}"/>\n'
        svg += f'        <text x="{legend_x + 8}" y="{legend_y + 3}" font-family="Inter, sans-serif" font-size="8" fill="#333">{series_name}</text>\n'

    svg += "    </svg>\n"
    return svg


def render_metric_cards(metrics_dict: dict, color_mapping: dict = None) -> str:
    """Render metric cards with z-score bars and percentile rankings.

    Args:
        metrics_dict: Dictionary of metrics to render
        color_mapping: Optional dict mapping metric names to CSS classes for background colors

    Returns:
        HTML string containing metric cards
    """
    if color_mapping is None:
        color_mapping = {}

    cards_html = ""
    for metric_name, metric in metrics_dict.items():
        metric = reverse_metric_if_needed(metric)

        z_score = metric.z_score
        bar_end_position = ((z_score + 2) / 4) * 100
        bar_end_position = max(0, min(100, bar_end_position))

        bar_start = 50
        bar_width = abs(bar_end_position - bar_start)
        bar_left = min(bar_start, bar_end_position)

        secondary_tick_html = ""
        if metric.secondary_z_score is not None:
            secondary_position = ((metric.secondary_z_score + 2) / 4) * 100
            secondary_position = max(0, min(100, secondary_position))
            secondary_tick_html = (
                f'<div style="position: absolute; left: {secondary_position}%; top: 100%; '
                f'width: 0; height: 0; border-left: 4px solid transparent; border-right: 4px solid transparent; '
                f'border-bottom: 6px solid #8e44ad; transform: translateX(-50%);" title="Previous"></div>'
            )

        # Color (card background/border and bar fill) by percentile rank (1 = best
        # after reversal above): bottom quartile-ish (rank >= 18/24) is red, top
        # quintile-ish (rank <= 5/24) is green, everything else is neutral gray.
        if metric.percentile_total:
            rank_fraction = metric.percentile_order / metric.percentile_total
        else:
            rank_fraction = 0.5

        if rank_fraction >= 18 / 24:
            card_bg_color = "#e3c8c6"
            card_border_color = "#e74c3c"
            card_border_width = "9px"
            value_text_color = "#c0392b"
        elif rank_fraction <= 5 / 24:
            card_bg_color = "#c1dccb"
            card_border_color = "#27ae60"
            card_border_width = "9px"
            value_text_color = "#1e8449"
        else:
            card_bg_color = "#f8fafc"
            card_border_color = "#666666"
            card_border_width = "6px"
            value_text_color = "#0f1923"

        # Thin border around the whole card: same color as the rank color, double
        # the original 1px thickness.
        card_thin_border_width = "2px"

        bar_color = card_border_color

        # Use label2 as the main display name
        display_name = metric.label2 if metric.label2 else metric.label

        # Use label as the description
        label_text = metric.label if metric.label else ""
        percentile_text = f"P: ({metric.percentile_order}/{metric.percentile_total})"

        background_class = color_mapping.get(metric_name, "metric-card")
        card_class = f"metric-card {background_class}"

        if metric.show_as_percentage and metric.value_pg is not None:
            display_value = f"{metric.value_pg * 100:.1f}%"
        else:
            display_value = f"{metric.value_pg:.2f}"

        cards_html += f"""
            <div class="{card_class}" style="background-color: {card_bg_color}; border: {card_thin_border_width} solid {card_border_color}; border-left-width: {card_border_width};">
                <div class="metric-card-name">{display_name}</div>
                <div class="metric-card-value" style="color: {value_text_color};">{display_value}</div>
                <div class="metric-card-zscore">
                    <span class="metric-label-left">{label_text}</span>
                    <span class="metric-percentile-right">{percentile_text}</span>
                </div>
                <div class="metric-card-bar">
                    <div class="metric-card-bar-background">
                        <div class="metric-card-bar-center" style="position: absolute; left: 50%; top: -3px; width: 2px; height: 11px; background-color: #333333; transform: translateX(-50%);" title="Average"></div>
                        <div class="metric-card-bar-fill" style="left: {bar_left}%; width: {bar_width}%; background-color: {bar_color};"></div>
                        {secondary_tick_html}
                    </div>
                </div>
                <div class="metric-card-bar-labels">
                    <span class="metric-card-bar-label-left">{metric.bar_label_low}</span>
                    <span class="metric-card-bar-label-right">{metric.bar_label_high}</span>
                </div>
            </div>
        """
    return cards_html
