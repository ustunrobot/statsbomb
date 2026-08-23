"""Radar chart generation using ReportLab Drawing."""

from reportlab.graphics.shapes import Drawing, Circle, Polygon, String, Line
from reportlab.lib import colors
import math
from reportlab.lib.units import inch


from .report_definition import *
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak

def get_color(values: ChartValue) -> colors.Color:
    percentile = values.percentile
    total = values.percentile_total
    if percentile / total > 0.8:
        return colors.HexColor("#e90c0c")
    if percentile / total > 0.6:
        return colors.HexColor("#e96c0c")
    if percentile / total > 0.4:
            return colors.HexColor("#536fe0")
    if percentile / total > 0.2:
        return colors.HexColor("#4c9510")

    return colors.HexColor("#D619C3")


def create_player_radar_chart(styles, radar_params: ChartParams = None) -> Table:
    """
    Create a radar chart for player performance metrics using ReportLab Drawing.

    Args:
        radar_params: RadarParams object with styling and data configuration
        metrics: Dict with metric names as keys and values 0-100 (legacy)
        size: Size of the drawing in points

    Returns:
        ReportLab Drawing object
    """
    
    if radar_params is not None:
        size = int(radar_params.outer_table_size) if radar_params.outer_table_size else 200
        radar_type = radar_params.chart_type if radar_params.chart_type else "Circular"
        inner_size = int(0.8 * size)

    
    drawing = Drawing(inner_size, inner_size)
    center_x = inner_size / 2
    center_y = inner_size / 2
    max_radius = inner_size / 2.5

    # Calculate polygon points first (needed for both grid types)
    num_metrics = len(radar_params.values)
    angles = [2 * math.pi * i / num_metrics - math.pi / 2 for i in range(num_metrics)]
    categories = list(radar_params.values.keys())
    
    # Draw grid based on radar type
    if radar_type == "Circular":
        # Draw concentric circles fixed number (3)
        for i in range(1, 4):
            radius = (i / 3) * max_radius
            circle = Circle(center_x, center_y, radius,
                           strokeColor=colors.HexColor('#e0e0e0'),
                           strokeWidth=0.5,
                           fillColor=None)
            drawing.add(circle)
    else:
        # Draw spider web with lines
        # Draw concentric circles connected by lines
        for i in range(1, 5):
            radius = (i / 4) * max_radius
            # Draw polygon connecting points on this radius
            circle_points = []
            for angle in angles:
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                circle_points.append((x, y))

            flat_points = [coord for point in circle_points for coord in point]
            circle_poly = Polygon(flat_points,
                                 strokeColor=colors.HexColor('#e0e0e0'),
                                 strokeWidth=0.5,
                                 fillColor=None)
            drawing.add(circle_poly)

    # Add radial axis lines
    for angle in angles:
        x_end = center_x + max_radius * math.cos(angle)
        y_end = center_y + max_radius * math.sin(angle)
        line = Line(center_x, center_y, x_end, y_end,
                   strokeColor=colors.HexColor('#e0e0e0'),
                   strokeWidth=0.5)
        drawing.add(line)

    # Calculate points for the radar polygon
    points = []
    for angle, category in zip(angles, categories):
        # Use the max_val from the radar_value_object for scaling
        max_val = radar_params.values[category].max_val
        val = radar_params.values[category].chart_val
        radius = (val / max_val) * max_radius
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))

    # Draw the polygon (filled area)
    # Flatten the list of tuples into a single list for ReportLab
    flat_points = [coord for point in points for coord in point]
    polygon = Polygon(flat_points,
                     strokeColor=colors.HexColor("#4379CA"),
                     strokeWidth=1.0,
                     fillColor=colors.HexColor("#78A3B7"),
                     fillOpacity=0.4)
    drawing.add(polygon)

    # Draw the data points
    for row_number, (x, y) in enumerate(points):
        point_color = get_color(list(radar_params.values.values())[row_number])
        circle = Circle(x, y, 2.5,                        
                       strokeColor=colors.HexColor("#F9F9FC"),
                       strokeWidth=1.0,
                       fillColor=point_color,
                       fillOpacity=1.0)
        drawing.add(circle)

    # Calculate points for the avg polygon
    points = []
    for angle, category in zip(angles, categories):
        # Use the max_val from the radar_value_object for scaling
        max_val = radar_params.values[category].max_val
        val = radar_params.values[category].avg_val
        radius = (val / max_val) * max_radius
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))

    # Draw the polygon (filled area)
    # Flatten the list of tuples into a single list for ReportLab
    flat_points = [coord for point in points for coord in point]
    polygon = Polygon(flat_points,
                        strokeColor=colors.HexColor("#8E9AAC"),
                        strokeDashArray=[3,3],
                        strokeWidth=1.0,
                        fillColor=colors.HexColor("#CFD2D3"),
                        fillOpacity=0.2)
    drawing.add(polygon)
    # Add category labels with percentile values
    label_margin = 15
    for i, (angle, category) in enumerate(zip(angles, categories)):
        label_radius = max_radius + label_margin
        label_x = center_x + label_radius * math.cos(angle)
        label_y = center_y + label_radius * math.sin(angle)
        # Add category label
        text = String(label_x, label_y+2, category,
                     textAnchor='middle',
                     fontSize=6,
                     fontName="Roboto_Condensed-Bold",
                     fillColor=colors.HexColor("#646363"))
        drawing.add(text)

        # Add percentile value below the label
        radar_val = radar_params.values[category]
        val_text = f"{radar_val.chart_val} | {radar_val.avg_val}"
        percentile_text = f"P{int(radar_val.percentile * 100 / radar_val.percentile_total)}%"        
        percentile_color = get_color(radar_val)

        # Position percentile below the category label
        percentile_y = label_y - 3
        percentile = String(label_x, percentile_y, percentile_text,
                           textAnchor='middle',
                           fontName="Roboto-Light",
                           fontSize=5,
                           fillColor=colors.HexColor('#333333'))
        drawing.add(percentile)
        val_y = label_y - 8
        val = String(label_x, val_y, val_text,
                            textAnchor='middle',
                            fontName="Roboto-Bold",
                            fontSize=5,
                            fillColor=percentile_color)
        drawing.add(val)

        
        radar_data = [
            [   P(radar_params.title, font="Roboto_Condensed-Bold", color="#4B6EA2", alignment=TA_CENTER)
            ],
            [ drawing       
            ],
            [   Paragraph(
                    f"{('(Dashed line shows the averages)')}",
                    styles['chartBottom']
                    )
            ],
            ]
        
        radar_table = Table(radar_data, colWidths=[size], rowHeights=[int(0.1 * size), inner_size + label_margin, int(0.1 * size)])
        radar_table.setStyle(TableStyle([
            #('GRID', (0, 0), (-1, -1), 1, COLOR_BORDER_LIGHT),
            ('BACKGROUND', (0, 0), (-1, -1), radar_params.outer_table_bg_color),            
            ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_HEADER_TEXT),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('BORDERS', (0, 0), (-1, -1), 1),
            ('LINEBELOW', (0, -1), (0, -1), 0.2, radar_params.outer_table_border_color),
            ('LINEABOVE', (0, 0), (0, 0), 0.2, radar_params.outer_table_border_color),
            ('LINEBEFORE', (0, 0), (0, -1), 0.2, radar_params.outer_table_border_color),
            ('LINEAFTER', (0, 0), (0, -1), 0.2, radar_params.outer_table_border_color),


        ]))
        

    return radar_table
