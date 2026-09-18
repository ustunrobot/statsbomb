#!/usr/bin/env python3
"""Section 1: Report title section renderer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.metrics import Metric

section_data = {}

def get_styles() -> str:
    """Return CSS styles for the report."""
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

    .a4-container {
      width: 210mm;
      background: white;
      margin: 0 auto;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      overflow: visible;
    }

    .cover {
      display: grid;
      grid-template-columns: 6px 1fr;
      min-height: 160px;
      background: var(--ink);
      color: white;
      padding: 40px 48px 36px 42px;
      gap: 0 24px;
      align-items: start;
    }

    .cover.player {
      min-height: 80px;
      padding: 20px 24px 18px 21px;
    }

    .cover-stripe {
      background: var(--accent);
    }

    .cover-content {
    }

    .cover-eyebrow {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      font-weight: 500;
      letter-spacing: .12em;
      color: rgba(255,255,255,.5);
      text-transform: uppercase;
      margin-bottom: 10px;
    }

    .cover.player .cover-eyebrow {
      margin-bottom: 5px;
    }

    .cover-title {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 28px;
      font-weight: 700;
      line-height: 1.1;
      margin-bottom: 8px;
      color: #6fa0e8;
    }

    .cover.player .cover-title {
      margin-bottom: 4px;
    }

    .cover-title span {
      color: #6fa0e8;
    }

    .cover-subtitle {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: rgba(255,255,255,.6);
      margin-top: 6px;
    }

    .cover.player .cover-subtitle {
      margin-top: 3px;
    }

    .cover-meta {
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 13px;
      color: rgba(255,255,255,.55);
      margin-top: 16px;
      margin-bottom: 16px;
      display: flex;
      gap: 24px;
    }

    .cover.player .cover-meta {
      margin-top: 8px;
      margin-bottom: 8px;
      gap: 12px;
    }

    .cover-meta b {
      color: rgba(255,255,255,.8);
    }

    @media print {
      body {
        background: white;
        padding: 0;
      }
      .a4-container {
        width: 100%;
        box-shadow: none;
        margin: 0;
      }
    }
    </style>
    """


def render_report_title_section(all_metrics: dict, report_type: str = "team", player_name: str = None, sample_size: int = None) -> str:
    """Render the report title section using cover styling."""
    cover_class = "cover"
    if report_type == "player":
        cover_class = "cover player"

    title = player_name if report_type == "player" else all_metrics.get('team_name')

    html = f"""
    <section class="{cover_class}">
        <div class="cover-stripe"></div>
        <div class="cover-content">
            <div class="cover-eyebrow">
                {"Player Intelligence Report" if report_type == "player" else "Opponent Intelligence Report"}
            </div>
            <h1 class="cover-title">
                {title}
            </h1>
            <div class="cover-subtitle">
                {all_metrics.get('league')} - {all_metrics.get('season')} - StatsBomb Data
            </div>
            <div class="cover-meta">
                <span><b>{all_metrics.get('matches')}</b> Matches Analyzed</span>
                <span><b>{all_metrics.get('total_teams')}</b> Teams in League</span>
                {f'<span><b>{sample_size}</b> Players Compared</span>' if sample_size is not None else ''}
            </div>
        </div>
    </section>
    """
    return html


def render_full_document(section_data: dict) -> str:
    """Render a complete HTML document with A4 formatting."""
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Opponent Intelligence Report</title>
        {get_styles()}
    </head>
    <body>
        <div class="a4-container">
            {render_report_title_section(section_data)}
        </div>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    # Test the function
    html_output = render_full_document(section_data)
    print(html_output)
