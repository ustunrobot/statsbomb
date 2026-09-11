#!/usr/bin/env python3
"""Section 6: Pressing locations heatmap."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

section_data = {}

section_data['Team'] = "Port Vale FC"

# Pressing heatmap data: 10x10 grid representing pitch locations (0-100 scale)
# Each cell contains intensity value (0-100) representing pressing frequency
section_data['Pressing_Heatmap'] = {
    'width': 100,
    'height': 100,
    'grid': [
        [5, 8, 12, 15, 55, 15, 12, 8, 5, 3],  # Row 0 (low intensity - attacking third)
        [8, 12, 18, 25, 78, 25, 18, 12, 8, 5],
        [12, 18, 28, 35, 95, 75, 65, 45, 12, 8],
        [18, 28, 42, 55, 65, 55, 42, 55, 18, 12],
        [25, 38, 52, 68, 85, 68, 52, 66, 25, 18],  # Row 4 (midfield - high intensity)
        [18, 28, 42, 55, 65, 55, 42, 28, 18, 12],
        [12, 18, 28, 35, 40, 35, 28, 18, 12, 8],
        [8, 12, 18, 25, 28, 25, 18, 12, 8, 5],
        [5, 8, 12, 15, 18, 15, 12, 8, 5, 3],
        [2, 5, 8, 10, 12, 10, 8, 5, 2, 1],  # Row 9 (very low - own penalty area)
    ]
}


def create_pitch_background() -> str:
    """Create an SVG pitch background with correct proportions."""
    # 20% bigger: 250 * 1.2 = 300, 170 * 1.2 = 204
    pitch_width = 300
    pitch_height = 204
    line_color = "#cccccc"

    # Standard football pitch: 100 yards wide x 68.5 yards tall
    # Calculate pixels per yard for consistent scaling
    px_per_yard_w = pitch_width / 100
    px_per_yard_h = pitch_height / 68.5

    # Calculate all elements based on standard yards, then convert to pixels
    center_circle_r = int(10 * px_per_yard_h)  # 10 yards radius
    penalty_width = int(22 * px_per_yard_w)  # 22 yards wide (half of 44)
    penalty_height = int(36 * px_per_yard_h)  # 36 yards deep (double of 18)
    goal_width = int(9 * px_per_yard_w)  # 9 yards wide (half of 18)
    goal_height = int(12 * px_per_yard_h)  # 12 yards deep (double of 6)

    # Calculate Y positions (centered on the center line)
    center_y = pitch_height // 2
    penalty_y = int(center_y - penalty_height / 2)
    goal_y = int(center_y - goal_height / 2)

    svg = f"""
    <svg width="{pitch_width}" height="{pitch_height}" viewBox="0 0 {pitch_width} {pitch_height}" xmlns="http://www.w3.org/2000/svg" class="pitch-svg">
        <!-- Pitch background -->
        <rect width="{pitch_width}" height="{pitch_height}" fill="#f9f9f9"/>

        <!-- Pitch lines -->
        <!-- Halfway line -->
        <line x1="{pitch_width//2}" y1="0" x2="{pitch_width//2}" y2="{pitch_height}" stroke="{line_color}" stroke-width="1"/>

        <!-- Center circle -->
        <circle cx="{pitch_width//2}" cy="{pitch_height//2}" r="{center_circle_r}" fill="none" stroke="{line_color}" stroke-width="1"/>

        <!-- Center spot -->
        <circle cx="{pitch_width//2}" cy="{pitch_height//2}" r="2" fill="{line_color}"/>

        <!-- Left penalty area -->
        <rect x="0" y="{penalty_y}" width="{penalty_width}" height="{penalty_height}" fill="none" stroke="{line_color}" stroke-width="1"/>

        <!-- Right penalty area -->
        <rect x="{pitch_width - penalty_width}" y="{penalty_y}" width="{penalty_width}" height="{penalty_height}" fill="none" stroke="{line_color}" stroke-width="1"/>

        <!-- Left goal area -->
        <rect x="0" y="{goal_y}" width="{goal_width}" height="{goal_height}" fill="none" stroke="{line_color}" stroke-width="1"/>

        <!-- Right goal area -->
        <rect x="{pitch_width - goal_width}" y="{goal_y}" width="{goal_width}" height="{goal_height}" fill="none" stroke="{line_color}" stroke-width="1"/>
    </svg>
    """
    return svg


def create_heatmap_overlay(section_data: dict) -> str:
    """Create heatmap overlay on top of pitch."""
    heatmap_data = section_data.get('Pressing_Heatmap', {})
    grid = heatmap_data.get('grid', [])
    width = heatmap_data.get('width', 100)
    height = heatmap_data.get('height', 100)

    pitch_width = 300
    pitch_height = 204

    if not grid:
        return ""

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    cell_width = pitch_width / cols
    cell_height = pitch_height / rows

    # Color mapping with proportional scaling
    def intensity_to_color(intensity):
        """Convert intensity (0-100) to heatmap color with proportional scaling.

        0-30: Dark blue to light blue
        31-40: Light blue to mid green
        40-60: Mid green to yellow
        60-70: Yellow to orange
        70-100: Orange to red
        """
        intensity = max(0, min(100, intensity))  # Clamp to 0-100

        if intensity <= 30:
            # Dark blue (#0000CC) to light blue (#ADD8E6)
            ratio = intensity / 30
            r = int(0 + (173 - 0) * ratio)
            g = int(0 + (216 - 0) * ratio)
            b = int(204 + (230 - 204) * ratio)
        elif intensity <= 40:
            # Light blue (#ADD8E6) to mid green (#32CD32)
            ratio = (intensity - 30) / 10
            r = int(173 + (50 - 173) * ratio)
            g = int(216 + (205 - 216) * ratio)
            b = int(230 + (50 - 230) * ratio)
        elif intensity <= 60:
            # Mid green (#32CD32) to yellow (#FFFF00)
            ratio = (intensity - 40) / 20
            r = int(50 + (255 - 50) * ratio)
            g = int(205 + (255 - 205) * ratio)
            b = int(50 + (0 - 50) * ratio)
        elif intensity <= 70:
            # Yellow (#FFFF00) to orange (#FF8C00)
            ratio = (intensity - 60) / 10
            r = int(255 + (255 - 255) * ratio)
            g = int(255 + (140 - 255) * ratio)
            b = int(0 + (0 - 0) * ratio)
        else:
            # Orange (#FF8C00) to red (#FF0000)
            ratio = (intensity - 70) / 30
            r = int(255 + (255 - 255) * ratio)
            g = int(140 + (0 - 140) * ratio)
            b = int(0 + (0 - 0) * ratio)

        return f"#{r:02x}{g:02x}{b:02x}"

    heatmap_svg = '<svg class="heatmap-overlay" width="300" height="204" viewBox="0 0 300 204" xmlns="http://www.w3.org/2000/svg" style="position: absolute; top: 0; left: 0; mix-blend-mode: normal;">\n'

    for row_idx, row in enumerate(grid):
        for col_idx, intensity in enumerate(row):
            x = col_idx * cell_width
            y = row_idx * cell_height
            color = intensity_to_color(intensity)
            opacity = intensity / 100 * 0.8  # Max opacity 0.8

            heatmap_svg += f'        <rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" fill="{color}" opacity="{opacity}"/>\n'

    heatmap_svg += '    </svg>\n'
    return heatmap_svg


def render_pressing_heatmap_section(section_data: dict) -> str:
    """Render section 6 with pressing locations heatmap and side box."""
    pitch_svg = create_pitch_background()
    heatmap_svg = create_heatmap_overlay(section_data)

    html = f"""
    <section class="pressing-heatmap-section">
        <div class="section-container">
            <h2 class="section-title">Pressing Locations</h2>
            <p class="section-subtitle">Team pressing intensity by pitch location for {section_data.get('Team', 'Team')}</p>

            <div class="heatmap-container">
                <div class="pitch-wrapper">
                    {pitch_svg}
                    {heatmap_svg}
                </div>
                <div class="stats-box"></div>
            </div>
        </div>
    </section>
    """
    return html


def get_styles() -> str:
    """Return CSS styles for section 6."""
    return """
    <style>
    .pressing-heatmap-section {
      padding: 40px 48px;
      background: white;
      border-top: 1px solid #e5e5e5;
      page-break-after: always;
    }

    .section-container {
      max-width: 1000px;
    }

    .section-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 24px;
      font-weight: 700;
      color: var(--ink);
      margin-bottom: 4px;
    }

    .section-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: #999;
      margin-bottom: 24px;
    }

    .heatmap-container {
      display: flex;
      justify-content: flex-start;
      align-items: flex-start;
      background: transparent;
      padding: 0;
      gap: 24px;
    }

    .pitch-wrapper {
      position: relative;
      width: 300px;
      height: 204px;
      background: white;
      border-radius: 0;
      overflow: hidden;
      box-shadow: none;
      flex-shrink: 0;
    }

    .stats-box {
      width: 204px;
      height: 204px;
      border: 1px solid #d9d9d9;
      border-radius: 6px;
      background: white;
      flex-shrink: 0;
    }

    .pitch-svg {
      width: 100%;
      height: 100%;
    }

    .heatmap-overlay {
      width: 100%;
      height: 100%;
      mix-blend-mode: normal;
    }
    </style>
    """


if __name__ == "__main__":
    # Test the function
    html_output = render_pressing_heatmap_section(section_data)
    print(html_output)
