"""
Professional scouting intelligence report generation using ReportLab.

Design: Print-optimised professional report with teal/amber/red accent system.
Follows print-friendly guidelines with white/grey backgrounds and structured layouts.
"""

from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path
import os
import sys
from io import StringIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, KeepTogether, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

# Import shared utilities
from .report_definition import (
    get_styles, FONT_HEADER, FONT_HEADER_REGULAR, FONT_BODY, FONT_BODY_BOLD, FONT_BODY_EMPHASIS,
    COLOR_BG_PAGE, COLOR_BG_SECTION, COLOR_BG_SECONDARY, COLOR_TEXT_BODY,
    COLOR_TEXT_BODY_LIGHTER, COLOR_TEXT_MUTED, COLOR_BORDER_LIGHT, COLOR_BORDER_STRONG,
    COLOR_TEAL_PRIMARY, COLOR_TEAL_TINT, COLOR_TEAL_MID, COLOR_AMBER_PRIMARY,
    COLOR_AMBER_TINT, COLOR_AMBER_MID, COLOR_RED_PRIMARY, COLOR_RED_TINT,
    COLOR_HEADER_BG, COLOR_HEADER_TEXT
)
from .report_page_1 import create_page_1_cover
from .report_page_2 import create_page_2_basic_statistics
from .report_page_3 import create_page_3_buildup_analysis
from .report_page_4 import create_page_4_out_of_possession
from .report_page_5 import create_page_5_analysis


# ═════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════

def letter_space(text: str, gap: float = 1) -> str:
    """Add letter spacing between characters while preserving original spaces."""
    spaces = " " * int(gap)
    result = []
    for i, char in enumerate(text):
        result.append(char)
        # Add spacing between non-space characters only
        if i < len(text) - 1 and char != ' ' and text[i + 1] != ' ':
            result.append(spaces)
    return ''.join(result)


def create_section_label(text: str) -> Paragraph:
    """Create section label with teal accent."""
    styles = get_styles()
    return Paragraph(f"<b>{text}</b>", styles['SectionLabel'])


def create_container_content(label: str, value: str, label_style: str = 'SectionLabel') -> Table:
    """Create a container with label and value."""
    styles = get_styles()
    inner_data = [
        [Paragraph(label, styles[label_style])],
        [Paragraph(value, styles['BigNumber'])],
    ]
    inner_table = Table(inner_data, colWidths=[1.9 * inch])
    inner_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (0, 0), 0),
        ('BOTTOMPADDING', (0, 1), (0, 1), 0),
        ('BORDERS', (0, 0), (-1, -1), 0, colors.white),
    ]))
    return inner_table


def create_metric_box(label: str, value: str, bg_color=COLOR_BG_SECTION) -> Table:
    """
    Create a metric/stat box.

    Layout:
        Label (small, muted, ALL CAPS)
        Value (large, bold)
    """
    styles = get_styles()

    data = [
        [Paragraph(label.upper(), styles['SmallLabel'])],
        [Paragraph(value, styles['StatValue'])],
    ]

    table = Table(data, colWidths=[1.3 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('BORDER', (0, 0), (-1, -1), 1, COLOR_BORDER_LIGHT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))

    return table


def create_stat_comparison_row(label: str, your_value: float, your_bar: float,
                               opp_value: float, opp_bar: float) -> Table:
    """
    Create 3-column stat comparison row.

    Layout: [Your value + bar] | [Centre label] | [Bar + Opp value]
    """
    styles = get_styles()

    # Left side (your team - teal)
    your_pct = f"{your_value:.1%}" if isinstance(your_value, float) else str(your_value)
    your_bar_width = int(your_bar * 30) if your_bar <= 1 else int(30)

    # Right side (opponent - amber)
    opp_pct = f"{opp_value:.1%}" if isinstance(opp_value, float) else str(opp_value)
    opp_bar_width = int(opp_bar * 30) if opp_bar <= 1 else int(30)

    # Create bar visuals
    your_bar_html = "█" * your_bar_width
    opp_bar_html = "█" * opp_bar_width

    data = [
        [
            Paragraph(your_pct, styles['StatValue']),
            Paragraph(label, styles['SmallLabel']),
            Paragraph(opp_pct, styles['StatValue']),
        ]
    ]

    table = Table(data, colWidths=[1.2 * inch, 2.5 * inch, 1.2 * inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (0, -1), COLOR_TEAL_PRIMARY),
        ('TEXTCOLOR', (2, 0), (2, -1), COLOR_AMBER_PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    return table


def create_intelligence_card(tag: str, title: str, content: str,
                             tag_color=COLOR_TEAL_PRIMARY,
                             bg_color=COLOR_TEAL_TINT) -> Table:
    """
    Create an intelligence/note card with left accent border.

    Structure:
        border-left: 3px [tag_color]
        background: [bg_color]
        tag: 8px, color-coded
        title: card label
        content: body text
    """
    styles = get_styles()

    data = [
        [
            Paragraph(f"<font color='{tag_color.hexval()}' size='8'><b>{tag}</b></font>", styles['SmallLabel']),
        ],
        [
            Paragraph(f"<b>{title}</b>", styles['BodyText']),
        ],
        [
            Paragraph(content, styles['BodyText']),
        ],
    ]

    table = Table(data, colWidths=[6.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('BORDER', (0, 0), (-1, -1), 1, COLOR_BORDER_LIGHT),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))

    return table


def create_results_table(results: List[Dict]) -> Table:
    """
    Create a match results table.

    Columns: Date | Match | Result | Score | xG
    """
    styles = get_styles()

    # Header
    data = [[
        Paragraph("Date", styles['SmallLabel']),
        Paragraph("Match", styles['SmallLabel']),
        Paragraph("Result", styles['SmallLabel']),
        Paragraph("Score", styles['SmallLabel']),
    ]]

    # Sample rows (would be populated from actual data)
    for i in range(3):
        data.append([
            Paragraph("2024-08-15", styles['BodyText']),
            Paragraph("vs Opponent", styles['BodyText']),
            Paragraph("W", styles['BodyText']),
            Paragraph("3-1", styles['BodyText']),
        ])

    table = Table(data, colWidths=[1.2 * inch, 2.5 * inch, 1.2 * inch, 1.1 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_TEAL_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_HEADER_TEXT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 1, COLOR_BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLOR_BG_PAGE, COLOR_BG_SECTION]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    return table


def _create_bar_chart(percentage: float, color) -> str:
    """Create a simple text-based bar representation for tables."""
    if percentage <= 0:
        return "—"

    bar_length = int(percentage * 20)
    filled_width = bar_length * 2
    total_width = 40

    hex_color = color.hexval()
    bar_html = f"<font color='{hex_color}'>" + ("▮" * bar_length) + "</font>"

    return bar_html


# ═════════════════════════════════════════════════════════════════════════
# MAIN REPORT GENERATION
# ═════════════════════════════════════════════════════════════════════════

def generate_team_report(team_name: str, stats: Dict, output_dir: str = "data/outputs") -> str:
    """
    Generate professional scouting intelligence report PDF.

    Args:
        team_name: Team name
        stats: Statistics dict results
        output_dir: Directory to save PDF

    Returns:
        Path to generated PDF file
    """
    try:
        from reportlab.lib.pagesizes import letter
    except ImportError:
        print("reportlab required. Install with: pip install reportlab")
        return ""

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # PDF filename
    filename = f"opposition_report_{team_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = output_path / filename

    # Create PDF document (white page background)
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        topMargin=0,
        bottomMargin=0,
        leftMargin=0,
        rightMargin=0,
        title=f"Opposition Report - {team_name}"
    )

    story = []
    styles = get_styles()

    # ===== PAGE 1: COVER PAGE =====
    page_width = letter[0]   # Letter width = 8.5 inches
    page_height = letter[1]  # Letter height = 11 inches
    create_page_1_cover(story, team_name, stats, page_width)

    # ===== PAGE 2: BASIC STATISTICS =====
    create_page_2_basic_statistics(story, page_width)

    # ===== PAGE 3: BUILDUP ANALYSIS =====
    create_page_3_buildup_analysis(story, stats, page_width)

    # ===== PAGE 4: OUT OF POSSESSION =====
    create_page_4_out_of_possession(story, page_width)

    # ===== PAGE 5: ANALYSIS =====
    create_page_5_analysis(story, team_name, stats)

    # Build PDF
    doc.build(story)

    print(f"✓ Professional report saved to: {filepath}")
    return str(filepath)

