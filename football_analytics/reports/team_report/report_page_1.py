"""PAGE 1: Cover Page with team statistics and key metrics."""

from typing import Dict
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak

from ..report_common.report_definition import (
    get_styles, letter_space, COLOR_HEADER_TEXT, COLOR_BORDER_LIGHT, COLOR_BG_SECTION, COLOR_BG_PAGE,
    COLOR_TEAL_PRIMARY, COLOR_AMBER_PRIMARY, COLOR_RED_PRIMARY, COLOR_BORDER_STRONG,
    COLOR_TEAL_TINT, COLOR_AMBER_TINT, COLOR_RED_TINT, COLOR_TEXT_MUTED
)


def create_page_1_cover(story, v: Dict, page_width: float):
    """Create PAGE 1: Cover page with header, title, and key metrics."""
    styles = get_styles()

    # Black header bar (full width, report title + team name)
    cover_header_data = [
        [
            Paragraph(
                f"<font color='#B2D9D3'><b>{letter_space('EFL       League      Two')}</b></font>",
                styles['SectionLabel']
            ),
        ],
        [
            Paragraph(f"<b>{v["team"]}</b>", styles['PageTitle']),
        ],
        [
            Paragraph(f"<font color='#B2D9D3'>Analysis Prepared for Crawley Town FC — {datetime.now().strftime('%B %d, %Y')}</font>", styles['SectionLabel']),
        ],
    ]

    cover_header_table = Table(cover_header_data, colWidths=[page_width])
    cover_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_HEADER_TEXT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 48),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, 0), 32),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 32),
        ('BORDERS', (0, 0), (-1, -1), 0),
    ]))

    story.append(cover_header_table)
    story.append(Spacer(1, 1.2 * inch))

    # Team name and date on cover
    cover_content = [
        Paragraph(f"<font size='36'><b>Team Report</b></font>", styles['HeroNumber']),
        Spacer(10, 0.3 * inch),
        Spacer(10, 0.4 * inch),
        Paragraph(f"This report is based on", styles['SectionLabelBlack']),
        Spacer(10, 1.0 * inch),
    ]

    for item in cover_content:
        story.append(item)

    # Helper function to create container content with label and value
    def create_container_content(label: str, value: str, value2: str, label_style: str = 'SectionLabel' ):
        inner_data = [
            [Paragraph(label, styles[label_style])],
            [Paragraph(value, styles['BigNumber'])],
            [Paragraph(value2, styles['MetaText'])],
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

    # Three content containers with spacing between them
    col_width = 2.1 * inch
    spacer_width = 0.35 * inch
    container_data = [[
        create_container_content("MATCHES", f"{v["n_matches"]}", 
                                 f"processed {v["total_n_matches"]} matches for team comparisons", 
                                 label_style='SectionLabelTeal'),
        Paragraph("", styles['BodyText']),
        create_container_content("EVENTS", f"{v["n_events"]}", 
                                 f"processed {v["total_n_events"]} events for team comparisons",
                                 label_style='SectionLabelAmber'),
        Paragraph("", styles['BodyText']),
        create_container_content("ADVANCED METRICS", f"{v["n_metrics"]}", "Quantitative indicators derived from event data", label_style='SectionLabelRed'),
    ]]

    containers = Table(container_data, colWidths=[col_width, spacer_width, col_width, spacer_width, col_width])
    containers.setStyle(TableStyle([
        ('BOX', (0, 0), (0, -1), 1, COLOR_BORDER_LIGHT),
        ('BOX', (2, 0), (2, -1), 1, COLOR_BORDER_LIGHT),
        ('BOX', (4, 0), (4, -1), 1, COLOR_BORDER_LIGHT),
        ('BACKGROUND', (0, 0), (0, -1), COLOR_BG_SECTION),
        ('BACKGROUND', (2, 0), (2, -1), COLOR_BG_SECTION),
        ('BACKGROUND', (4, 0), (4, -1), COLOR_BG_SECTION),
        ('LINEBEFORE', (0, 0), (0, -1), 2, COLOR_TEAL_PRIMARY),
        ('LINEBEFORE', (2, 0), (2, -1), 2, COLOR_AMBER_PRIMARY),
        ('LINEBEFORE', (4, 0), (4, -1), 2, COLOR_RED_PRIMARY),
        ('LEFTPADDING', (0, 0), (0, -1), 8),
        ('RIGHTPADDING', (0, 0), (0, -1), 8),
        ('LEFTPADDING', (2, 0), (2, -1), 8),
        ('RIGHTPADDING', (2, 0), (2, -1), 8),
        ('LEFTPADDING', (4, 0), (4, -1), 8),
        ('RIGHTPADDING', (4, 0), (4, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BORDERS', (1, 0), (1, -1), 0, colors.white),
        ('BORDERS', (3, 0), (3, -1), 0, colors.white),
    ]))
    story.append(containers)

    story.append(Spacer(2, 0.6 * inch))

    # Sub Section Title with teal line
    section1_title_data = [[
        Paragraph("", styles['BodyText']),
        Paragraph(f"{letter_space('BASIC.STATISTICS', 2)}", styles['CaptionAmber']),
        Paragraph("", styles['BodyText']),
    ]]

    section1_title_table = Table(section1_title_data, colWidths=[1.8 * inch, 1.5 * inch, 1.8 * inch])
    section1_title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),        
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (0, 0), 0.5, COLOR_AMBER_TINT),
        ('LINEBELOW', (-1, 0), (-1, 0), 0.5, COLOR_AMBER_TINT),
    ]))
    story.append(section1_title_table)
    story.append(Spacer(0.5, 0.3 * inch))

    # Sub Section Title with teal line
    section2_title_data = [[
        Paragraph("", styles['BodyText']),
        Paragraph(f"{letter_space('BUILDUP.ANALYSIS', 2)}", styles['CaptionTeal']),
        Paragraph("", styles['BodyText']),
    ]]

    section2_title_table = Table(section2_title_data, colWidths=[1.8 * inch, 1.5 * inch, 1.8 * inch])
    section2_title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),        
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (0, 0), 0.5, COLOR_TEAL_TINT),
        ('LINEBELOW', (-1, 0), (-1, 0), 0.5, COLOR_TEAL_TINT),
    ]))
    story.append(section2_title_table)
    story.append(Spacer(0.5, 0.3 * inch))

    section3_title_data = [[
            Paragraph("", styles['BodyText']),
            Paragraph(f"{letter_space('OUT.OF.POSSESSION', 2)}", styles['CaptionRed']),
            Paragraph("", styles['BodyText']),
        ]]
    
    section3_title_table = Table(section3_title_data, colWidths=[1.8 * inch, 1.5 * inch, 1.8 * inch])
    section3_title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),        
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (0, 0), 0.5, COLOR_RED_TINT),
        ('LINEBELOW', (-1, 0), (-1, 0), 0.5, COLOR_RED_TINT),
    ]))
    story.append(section3_title_table)
    story.append(Spacer(0.5, 0.3 * inch))

    section4_title_data = [[
            Paragraph("", styles['BodyText']),
            Paragraph(f"{letter_space('PLAYER.DATA', 2)}", styles['CaptionGray']),
            Paragraph("", styles['BodyText']),
        ]]
    
    section4_title_table = Table(section4_title_data, colWidths=[1.8 * inch, 1.5 * inch, 1.8 * inch])
    section4_title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),        
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (0, 0), 0.2, COLOR_BORDER_LIGHT),
        ('LINEBELOW', (-1, 0), (-1, 0), 0.2, COLOR_BORDER_LIGHT),
    ]))
    story.append(section4_title_table)
    story.append(Spacer(0.5, 0.3 * inch))
    story.append(PageBreak())
