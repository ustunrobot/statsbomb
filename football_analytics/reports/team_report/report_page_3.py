"""PAGE 3: Buildup Analysis with containers and image."""

import os
from typing import Dict
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak, Image

from ..report_common.report_definition import (
    get_styles, letter_space, COLOR_TEAL_TINT, COLOR_RED_TINT, COLOR_HEADER_TEXT, COLOR_BORDER_LIGHT,
    COLOR_BG_PAGE, COLOR_TEAL_MID
)


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


def create_page_3_buildup_analysis(story, v: Dict, page_width: float):
    """Create PAGE 3: Buildup Analysis with mini header and containers."""
    styles = get_styles()

    # Mini header with teal background
    mini_header_data = [
        [
            Paragraph(
                f"{letter_space('Buildup')} . {letter_space('Analysis')}",
                styles['SectionLabelTeal']
            ),
        ],
    ]

    mini_header_table = Table(mini_header_data, colWidths=[page_width])
    mini_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_TEAL_TINT),
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
    story.append(Spacer(1, 0.4 * inch))

    # Sub Section Title with teal line
    section_title_data = [[
        Paragraph(f"{letter_space('STYLE.OF.PLAY', 2)}", styles['CardLabelTeal']),
        Paragraph("", styles['BodyText']),
    ]]

    section_title_table = Table(section_title_data, colWidths=[1.3 * inch, 6.2 * inch])
    section_title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),        
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (1, 0), (1, 0), 0.5, COLOR_TEAL_MID),
    ]))
    story.append(section_title_table)
    story.append(Spacer(1, 0.4 * inch))

    # Two-container layout with spacing
    col_width_2 = 2.5 * inch
    spacer_width_2 = 0.5 * inch

    # First container with image (original aspect ratio)
    container_1 = None
    if os.path.exists("all_positions_median.png"):
        try:
            from PIL import Image as PILImage
            viz_path = os.path.abspath("all_positions_median.png")

            # Get original image dimensions to maintain aspect ratio
            pil_img = PILImage.open(viz_path)
            img_width, img_height = pil_img.size
            aspect_ratio = img_width / img_height

            # Set width and calculate height to preserve aspect ratio
            display_width = 2.0 * inch
            display_height = display_width / aspect_ratio

            shape_image = Image(viz_path, width=display_width, height=display_height)
            container_1 = shape_image
        except Exception as e:
            print(f"Error loading image: {e}")
            container_1 = create_container_content("BUILD-UP PHASE", f"Error: {str(e)}", label_style='SectionLabelTeal')

    if container_1 is None:
        container_1 = create_container_content("BUILD-UP PHASE", "No image", label_style='SectionLabelTeal')

    container_data_2 = [[
        container_1,
        Paragraph("", styles['BodyText']),  # Spacer
        create_container_content("SHAPE", f"{v.get('shape', {}).get('back_shape', 'N/A')}", label_style='SectionLabelRed'),
    ]]

    containers_2 = Table(container_data_2, colWidths=[col_width_2, spacer_width_2, col_width_2])
    containers_2.setStyle(TableStyle([
        ('BOX', (0, 0), (0, -1), 1, COLOR_BORDER_LIGHT),
        ('BOX', (2, 0), (2, -1), 1, COLOR_BORDER_LIGHT),
        ('BACKGROUND', (0, 0), (0, -1), COLOR_BG_PAGE),
        ('BACKGROUND', (2, 0), (2, -1), COLOR_BG_PAGE),
        ('LINEBEFORE', (0, 0), (0, -1), 2, COLOR_TEAL_TINT),
        ('LINEBEFORE', (2, 0), (2, -1), 2, COLOR_RED_TINT),
        ('LEFTPADDING', (0, 0), (0, -1), 8),
        ('RIGHTPADDING', (0, 0), (0, -1), 8),
        ('LEFTPADDING', (2, 0), (2, -1), 8),
        ('RIGHTPADDING', (2, 0), (2, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BORDERS', (1, 0), (1, -1), 0, colors.white),
    ]))
    story.append(containers_2)
    story.append(PageBreak())
