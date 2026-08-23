"""PAGE 2: Basic Statistics mini header page."""

from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import HorizontalBarChart

from ..report_common.report_definition import *

from typing import Dict
from pathlib import Path
import random

def section_title(title: str, color, styles) -> Table: 
    # Sub Section Title with teal line
    section_title_data = [[
        Paragraph(f"{letter_space(title, 2)}", styles['CardLabelTeal']),
        Paragraph("", styles['BodyText']),
    ]]
    
    section_title_table = Table(section_title_data, colWidths=[1.3 * inch, 5.5 * inch])
    section_title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),        
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (1, 0), (1, 0), 0.5, COLOR_TEAL_MID),
    ]))

    return section_title_table

def chart_row(data: float, label: str, styles, color, max_value) -> list:
    
    chart_data = [
                [Paragraph(f"{data:.1f}", styles['tableNumber'] ),
                Paragraph(f"{label}", styles['tableText']),
                Paragraph("")],
            ]

     
    bar_width = 0.6 * data / max_value

    chart_table = Table(chart_data, colWidths=[0.5 * inch, 0.7 * inch, bar_width * inch], rowHeights=[0.2 * inch])
    chart_table.setStyle(TableStyle([
        #('GRID', (0, 0), (-1, -1), 1, COLOR_BORDER_LIGHT),
        ('BACKGROUND', (0, 0), (1, -1), COLOR_HEADER_TEXT),
        ('BACKGROUND', (-1, 0), (-1, -1), color),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_BORDER_STRONG),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        
    ]))

    return chart_table

def chart_bars(data: Dict, title: str, styles) -> Table:

    # prepare the chart rows
    rows_container_data = []
    row_height = []
    available_colors = [
        COLOR_TEAL_MID,
        COLOR_TEAL_PRIMARY,
        COLOR_AMBER_PRIMARY,
        COLOR_BORDER_STRONG,
        COLOR_BORDER_LIGHT
    ]

    # Find max value in data
    max_value = max(data.values()) if data else 100

    for key, value in data.items():
        # Reset colors list if empty
        if not available_colors:
            available_colors = [
                COLOR_TEAL_MID,
                COLOR_TEAL_PRIMARY,
                COLOR_AMBER_PRIMARY,
                COLOR_BORDER_STRONG,
                COLOR_BORDER_LIGHT
            ]

        # Pick and remove a random color
        random_color = random.choice(available_colors)
        available_colors.remove(random_color)

        single_row = chart_row(value, key, styles=styles, color=random_color, max_value=max_value)
        rows_container_data.append([single_row])
        row_height.append(0.22 * inch)

    rows_container = Table(rows_container_data, colWidths=[1.9 * inch], rowHeights=row_height)    
    rows_container.setStyle(TableStyle([        
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_SECTION),
        ]))

    # chart + chart title
    titled_container_data = []
    titled_container_data.append([Paragraph(f"{letter_space(title)}", styles['chartTitle'])])
    titled_container_data.append([rows_container])

    titled_container = Table(titled_container_data, colWidths=[2 * inch])
    titled_container.setStyle(TableStyle([        
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        #('BORDERS', (0, 0), (-1, -1), 1),
        ]))
    # chart with outer border    
    bordered_container_data = []    
    bordered_container_data.append([titled_container])

    bordered_container = Table(bordered_container_data, colWidths=[2 * inch])
    bordered_container.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, COLOR_BORDER_LIGHT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),   
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_SECTION),

        ]))

    return bordered_container

def get_match_row(styles) -> Table:
    
    table_data = [[Paragraph("Newport County", styles['tableTextRight']), Paragraph("3:0", styles['score']), Paragraph("Rochdale", styles['tableTextLeft'])]]    
    ret_table = Table(table_data, colWidths=[1 * inch, 0.2 * inch, 1 * inch], rowHeights=[0.15 * inch])
    ret_table.setStyle(TableStyle([        
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),    
        ]))
    return ret_table

def get_last5_wld(styles) -> Table:

        r1 = 'W'
        r2 = 'L'
        r3 = 'D'
        r4 = 'W'
        r5 = 'W'

        table_data = [[Paragraph(f"{r1}", styles['CaptionAmber']), 
                       Paragraph(f"{r2}", styles['CaptionRed']), r3, r4, r5]]
        cw = 0.5 * inch
        ret_table = Table(table_data, colWidths=[cw, cw, cw, cw, cw])
        ret_table.setStyle(TableStyle([        
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),    
            ]))
        return ret_table
     
def get_last5(styles) -> Table:
        text = get_match_row(styles=styles)
        table_data = [[text], 
                      [text], [text], [text], [text]]
        rh = 0.15 * inch
        ret_table = Table(table_data, rowHeights=[rh, rh, rh, rh, rh])
        ret_table.setStyle(TableStyle([        
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),    
            ]))
        return ret_table

def create_page_2_basic_statistics(story, v: Dict, page_width: float):
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
    
    story.append(Spacer(1, 0.6 * inch))

    chart_list = {"League Average" : 100,
                  "Last Season" : 22.7,
                  "Current Season" : 13.0,
                  "Last 5 Matches" : 45.3
                  }

    chart_possession = chart_bars(chart_list, "POSSESSION %", styles=styles)
    #story.append(chart_possession)

    chart_list = {"League Average" : 88,
                      "Last Season" : 22.7,
                      "Current Season" : 13.0,
                      "Last 5 Matches" : 45.3
                      }
    
    chart_ppda = chart_bars(chart_list, "PPDA ", styles=styles)

    chart_list = {"League Average" : 2.3,
                    "Last Season" : 1.7,
                    "Current Season" : 3.0,
                    "Last 5 Matches" : 2.3
                    }
        
    chart_xG = chart_bars(chart_list, "xG", styles=styles)

    section1_table_data = [
                    [chart_ppda,
                    chart_possession,
                    chart_xG], 
                    [chart_ppda,
                    chart_possession,
                    chart_xG], 
                    ]
            
    section1_table = Table(section1_table_data, colWidths=[2.2 * inch, 2.2 * inch, 2.2 * inch], rowHeights=[1.4 * inch, 1.4 * inch])
    section1_table.setStyle(TableStyle([        
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),    
        ]))

    story.append(section1_table)

    story.append(Spacer(1, 0.6 * inch))
    
    s1 = section_title("LAST 5 GAMES", COLOR_TEAL_PRIMARY, styles=styles)
    story.append(s1)


    sw = Paragraph("W", styles['SectionLabelAmber'])
    sl = Paragraph("L", styles['SectionLabelTeal'])
    last5_table_data = [
                [get_last5(styles=styles),
                 get_last5_wld(styles=styles) ]
                ]
    last5_table = Table(last5_table_data, colWidths=[2.5 * inch, 3.5 * inch], rowHeights=[1.4 * inch])
    last5_table.setStyle(TableStyle([        
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),    
            ]))

    story.append(last5_table)


    story.append(PageBreak())

    
