"""PAGE 5: Analysis page with defensive formation, buildup patterns, and more."""

from typing import Dict
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from .report_definition import (
    get_styles, COLOR_HEADER_BG, COLOR_HEADER_TEXT, COLOR_BG_SECTION, COLOR_BG_PAGE,
    COLOR_BORDER_LIGHT, COLOR_TEAL_PRIMARY, COLOR_AMBER_PRIMARY, COLOR_TEAL_MID
)


def _create_bar_chart(value: float, color) -> str:
    """Create a simple bar chart representation as HTML."""
    bar_width = int(value * 30) if value <= 1 else 30
    return f"<font color='{color.hexval()}'>{'█' * bar_width}</font>"


def create_section_label(text: str) -> Paragraph:
    """Create section label with teal accent."""
    styles = get_styles()
    return Paragraph(f"<b>{text}</b>", styles['SectionLabel'])


def create_page_5_analysis(story, team_name: str, stats: Dict):
    """Create PAGE 5: Analysis page with team details and statistics."""
    styles = get_styles()

    # HEADER BAR (dark background)
    header_data = [[
        Paragraph(f"<b>{team_name}</b>", styles['PageTitle']),
    ]]

    header_table = Table(header_data, colWidths=[7.5 * inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_HEADER_BG),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_HEADER_TEXT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 32),
        ('RIGHTPADDING', (0, 0), (-1, -1), 32),
        ('TOPPADDING', (0, 0), (-1, -1), 22),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 22),
    ]))

    story.append(header_table)
    story.append(Spacer(1, 0.25 * inch))

    # Outer padding wrapper
    content_items = []

    # ===== DEFENSIVE FORMATION SECTION =====
    content_items.append(create_section_label("DEFENSIVE FORMATION"))
    content_items.append(Spacer(1, 0.12 * inch))

    back_shape = stats.shape.get("back_shape", "Unknown")
    confidence = stats.shape.get("back_shape_confidence", 0.0)
    gk_inv = stats.shape.get("gk_involvement", 0.0)

    # Formation metrics - flat table (no nesting)
    formation_data = [
        [
            Paragraph("<b>FORMATION</b>", styles['SmallLabel']),
            Paragraph("<b>CONFIDENCE</b>", styles['SmallLabel']),
        ],
        [
            Paragraph(back_shape, styles['StatValue']),
            Paragraph(f"{confidence:.0%}", styles['StatValue']),
        ],
    ]

    formation_table = Table(formation_data, colWidths=[3.25 * inch, 3.25 * inch])
    formation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_SECTION),
        ('BORDER', (0, 0), (-1, -1), 1, COLOR_BORDER_LIGHT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))

    content_items.append(formation_table)
    content_items.append(Spacer(1, 0.16 * inch))

    # GK Involvement note
    gk_text = f"GK Involvement: <b>{gk_inv:.1%}</b>"
    content_items.append(Paragraph(gk_text, styles['BodyText']))
    content_items.append(Spacer(1, 0.18 * inch))

    # ===== BUILDUP PATTERNS SECTION =====
    content_items.append(create_section_label("BUILDUP PATTERNS"))
    content_items.append(Spacer(1, 0.12 * inch))

    buildup_left = stats.shape.get("buildup_end_left", 0.0)
    buildup_center = stats.shape.get("buildup_end_center", 0.0)
    buildup_right = stats.shape.get("buildup_end_right", 0.0)

    # Buildup locations with bars
    buildup_data = [
        ["Location", "Percentage", "Distribution"],
        ["Left", f"{buildup_left:.1%}", Paragraph(_create_bar_chart(buildup_left, COLOR_AMBER_PRIMARY), styles['BodyText'])],
        ["Center", f"{buildup_center:.1%}", Paragraph(_create_bar_chart(buildup_center, COLOR_TEAL_MID), styles['BodyText'])],
        ["Right", f"{buildup_right:.1%}", Paragraph(_create_bar_chart(buildup_right, COLOR_TEAL_PRIMARY), styles['BodyText'])],
    ]

    buildup_table = Table(buildup_data, colWidths=[1.2 * inch, 1.2 * inch, 4 * inch])
    buildup_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_TEAL_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_HEADER_TEXT),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLOR_BG_PAGE, COLOR_BG_SECTION]),
        ('GRID', (0, 0), (-1, -1), 1, COLOR_BORDER_LIGHT),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    content_items.append(buildup_table)
    content_items.append(Spacer(1, 0.18 * inch))

    # ===== KEY PASSING PATTERNS SECTION =====
    content_items.append(create_section_label("KEY PASSING PATTERNS"))
    content_items.append(Spacer(1, 0.12 * inch))

    bp_pos_1 = stats.shape.get("backward_pass_position_1", "N/A")
    bp_count_1 = stats.shape.get("backward_pass_count_1", 0)
    bp_pos_2 = stats.shape.get("backward_pass_position_2", "N/A")
    bp_count_2 = stats.shape.get("backward_pass_count_2", 0)

    pass_data = [
        ["Rank", "Position", "Passes"],
        ["#1", bp_pos_1, str(bp_count_1)],
        ["#2", bp_pos_2, str(bp_count_2)],
    ]

    pass_table = Table(pass_data, colWidths=[0.8 * inch, 3.5 * inch, 1.7 * inch])
    pass_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_TEAL_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_HEADER_TEXT),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLOR_BG_PAGE, COLOR_BG_SECTION]),
        ('GRID', (0, 0), (-1, -1), 1, COLOR_BORDER_LIGHT),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    content_items.append(pass_table)
    content_items.append(Spacer(1, 0.18 * inch))

    # ===== BALL RECEIPT LOCATIONS SECTION =====
    content_items.append(create_section_label("BALL RECEIPT LOCATIONS"))
    content_items.append(Spacer(1, 0.12 * inch))

    medians = stats.shape.get("medians", {})
    if medians:
        # Create table data
        position_data = [["Position", "X Coord", "Y Coord", "Count"]]

        for position in sorted(medians.keys()):
            m = medians[position]
            count = m.get('count', 0)
            x = m.get('x', 0)
            y = m.get('y', 0)

            position_data.append([
                position[:25],
                f"{x:.1f}",
                f"{y:.1f}",
                str(count)
            ])

        pos_table = Table(position_data, colWidths=[3.2 * inch, 1.2 * inch, 1.2 * inch, 1.1 * inch])
        pos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_TEAL_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_HEADER_TEXT),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLOR_BG_PAGE, COLOR_BG_SECTION]),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER_LIGHT),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        content_items.append(pos_table)
    else:
        content_items.append(Paragraph("No positional data available", styles['BodyText']))

    # Add all content with proper padding
    for item in content_items:
        story.append(item)
