#!/usr/bin/env python3
"""Section 1 Landscape: Report title section renderer for A4 landscape."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from event_based.metrics import Metric

section_data = {}

def get_styles() -> str:
    """Return CSS styles for the report in landscape orientation."""
    return """
    <style>
    :root {
      --ink: #0f1923;
      --accent: #1a4fa3;
    }

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap');

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      background: #f5f5f5;
      padding: 20px;
      font-family: 'Inter', system-ui, sans-serif;
    }

    .a4-container-landscape {
      width: 297mm;
      background: white;
      margin: 0 auto;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      overflow: visible;
    }

    .cover-landscape {
      display: grid;
      grid-template-columns: 6px 1fr;
      min-height: 120px;
      background: var(--ink);
      color: white;
      padding: 30px 48px 24px 42px;
      gap: 0 24px;
      align-items: start;
    }

    .cover-landscape.player {
      min-height: 60px;
      padding: 15px 24px 12px 21px;
    }

    .cover-landscape-stripe {
      background: var(--accent);
    }

    .cover-landscape-content {
    }

    .cover-landscape-eyebrow {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      font-weight: 500;
      letter-spacing: .12em;
      color: rgba(255,255,255,.5);
      text-transform: uppercase;
      margin-bottom: 10px;
    }

    .cover-landscape.player .cover-landscape-eyebrow {
      margin-bottom: 5px;
    }

    .cover-landscape-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 28px;
      font-weight: 700;
      line-height: 1.1;
      margin-bottom: 8px;
      color: #6fa0e8;
    }

    .cover-landscape.player .cover-landscape-title {
      margin-bottom: 4px;
    }

    .cover-landscape-title span {
      color: #6fa0e8;
    }

    .cover-landscape-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: rgba(255,255,255,.6);
      margin-top: 6px;
    }

    .cover-landscape.player .cover-landscape-subtitle {
      margin-top: 3px;
    }

    .cover-landscape-position {
      color: #DAA520;
      font-weight: 600;
    }

    .cover-landscape-meta {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: rgba(255,255,255,.55);
      margin-top: 16px;
      margin-bottom: 16px;
      display: flex;
      gap: 24px;
    }

    .cover-landscape.player .cover-landscape-meta {
      margin-top: 8px;
      margin-bottom: 8px;
      gap: 12px;
    }

    .cover-landscape-meta b {
      color: rgba(255,255,255,.8);
    }

    @media print {
      body {
        background: white;
        padding: 0;
      }
      .a4-container-landscape {
        width: 100%;
        box-shadow: none;
        margin: 0;
      }
    }
    </style>
    """


def render_report_title_section_landscape(all_metrics: dict, report_type: str = "team", player_name: str = None, sample_size: int = None, player_position: str = None, minutes_threshold: int = None) -> str:
    """Render the report title section using landscape cover styling."""
    cover_class = "cover-landscape"
    if report_type == "player":
        cover_class = "cover-landscape player"

    title = player_name if report_type == "player" else all_metrics.get('team_name')

    if report_type == "player":
        if player_position:
            subtitle = f'<span class="cover-landscape-position">{player_position}</span> - {all_metrics.get("league")} - {all_metrics.get("season")} - StatsBomb Data'
        else:
            subtitle = f'{all_metrics.get("league")} - {all_metrics.get("season")} - StatsBomb Data'
    else:
        subtitle = f'{all_metrics.get("league")} - {all_metrics.get("season")} - StatsBomb Data'

    html = f"""
    <section class="{cover_class}">
        <div class="cover-landscape-stripe"></div>
        <div class="cover-landscape-content">
            <div class="cover-landscape-eyebrow">
                {"Player Intelligence Report" if report_type == "player" else "Opponent Intelligence Report"}
            </div>
            <h1 class="cover-landscape-title">
                {title}
            </h1>
            <div class="cover-landscape-subtitle">
                {subtitle}
            </div>
            <div class="cover-landscape-meta">
                <span><b>{all_metrics.get('matches')}</b> Matches Analyzed</span>
                <span><b>{all_metrics.get('total_teams')}</b> Teams in League</span>
                {f'<span><b>{sample_size}</b> Players in similar positions compared.</span>' if sample_size is not None else ''}
                {f'<span> (Excluded players who played less than <b>{int(minutes_threshold)}</b> min.)</span>' if minutes_threshold is not None else ''}
            </div>
        </div>
    </section>
    """
    return html


def render_full_document(section_data: dict) -> str:
    """Render a complete HTML document with A4 landscape formatting."""
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Opponent Intelligence Report</title>
        {get_styles()}
    </head>
    <body>
        <div class="a4-container-landscape">
            {render_report_title_section_landscape(section_data)}
        </div>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    # Test the function
    html_output = render_full_document(section_data)
    print(html_output)
