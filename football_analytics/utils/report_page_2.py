"""PAGE 2: Basic Statistics mini header page."""

from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak

from .report_definition import get_styles, letter_space, COLOR_AMBER_TINT, COLOR_HEADER_TEXT


def create_page_2_basic_statistics(story, page_width: float):
    """Create PAGE 2: Basic Statistics with mini header."""
    styles = get_styles()

    # Mini header with amber background
    mini_header_data = [
        [
            Paragraph(
                f"{letter_space('Basic')} . {letter_space('Statistics')}",
                styles['SectionLabelAmber']
            ),
        ],
    ]

    mini_header_table = Table(mini_header_data, colWidths=[page_width])
    mini_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_AMBER_TINT),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_HEADER_TEXT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 48),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('BORDERS', (0, 0), (-1, -1), 0),
    ]))

    story.append(mini_header_table)
    story.append(PageBreak())
