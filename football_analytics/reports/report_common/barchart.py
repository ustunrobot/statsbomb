from reportlab.lib import colors
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

def bar_data(key, value: ChartValue, cw, rh) -> Table:

    p = value.chart_val * 100 / value.max_val
    col = get_color(values=value)
    table_data = [[ ProgressBar(width=cw, height=rh, percentage=p, fill_color=col)]]
    table = Table(table_data, colWidths=[cw], rowHeights=rh)
    table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_SECTION),            
            ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_HEADER_TEXT),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
    return table

def text_data(key, value: ChartValue, cw, rh) -> Table:

    # make 3 columns for data     
    title = key
    data1 = value.chart_val
    data2 = value.avg_val

    table_data = [[P(text=title,
                     font="Roboto_Condensed-Regular",
                     size=6,
                     color="#666666",
                     alignment=TA_LEFT),

                    P(text=f"{data1}",
                        font="Roboto_Condensed-Bold",
                        size=6,
                        color='#333333',
                        alignment=TA_RIGHT),
                     P(text=f"avg {data2}",
                        font="Roboto_Condensed-Regular",
                        size=6,
                        color='#999999',
                        alignment=TA_RIGHT)                   
                   ]]
    table = Table(table_data, colWidths=[cw * 0.7, cw * 0.15, cw * 0.15], rowHeights=rh)
    table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_SECTION),            
            ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_HEADER_TEXT),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
    return table

def create_barchart(styles, chart_params: ChartParams = None) -> Table:

    col_width  = chart_params.outer_table_size    
    row_height = 10

    text1 = Paragraph(
                    f"{('Dashed line')}",
                    styles['chartBottom']
                )

    barchart_data = []
    rh = []
    for key in chart_params.values:
        td = text_data(key, chart_params.values[key], col_width * 0.95, row_height)
        barchart_data.append([td])        
        rh.append(row_height)
        bd = bar_data(key, chart_params.values[key], col_width * 0.95, row_height/2)
        barchart_data.append([bd])
        rh.append(row_height/2)
            
    barchart_table = Table(barchart_data, colWidths=[col_width], rowHeights=rh)
    barchart_table.setStyle(TableStyle([
        #('GRID', (0, 0), (-1, -1), 1, COLOR_BORDER_LIGHT),
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_SECTION),            
        ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_HEADER_TEXT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('BORDERS', (0, 0), (-1, -1), 1),
        ('LINEBELOW', (0, -1), (0, -1), 0.5, COLOR_BORDER_LIGHT),
        ('LINEABOVE', (0, 0), (0, 0), 0.5, COLOR_BORDER_LIGHT),
        ('LINEBEFORE', (0, 0), (0, -1), 0.5, COLOR_BORDER_LIGHT),
        ('LINEAFTER', (0, 0), (0, -1), 0.5, COLOR_BORDER_LIGHT),
        ]))
    return barchart_table
