from reportlab.lib import colors
from .report_definition import *
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak



def bar_data(key, value: ChartValue, cw, rh) -> Table:
    normalization = "SD"    

    if normalization == "SD":
        zscore = (value.chart_val - value.avg_val) / value.std_dev
        if zscore < -3:
            zscore = -3
        if zscore > 3:
            zscore = 3
        p = (zscore + 3) * 100 / 6
        avg_p = 50
    else:
        p = (value.chart_val - value.min_val) * 100 / (value.max_val - value.min_val)
        avg_p = (value.avg_val - value.min_val) * 100 / (value.max_val - value.min_val)

    if value.reverse == 1:
        p = 100 - p
        avg_p = 100 - avg_p

    col = get_color(values=value)
    table_data = [[ ProgressBar(width=cw, height=rh, percentage=p, fill_color=col, average_percentage=avg_p, reverse = value.reverse)]]
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

def section_data(group_name, cw, rh) -> Table:
    
    table_data = [[ P(text=group_name,
                     font="Roboto_Condensed-Bold",
                     size=6,
                     color="#1F8FD4",
                     leading=7,
                     alignment=TA_LEFT)
                ]]
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
    data3 = int(value.percentile * 100 / value.percentile_total)

    table_data = [[P(text=title,
                     font="Roboto_Condensed-Light",
                     size=6,
                     color="#444444",
                     leading=7,
                     alignment=TA_LEFT),

                    P(text=f"{data1:.2f}",
                        font="Roboto_Condensed-Bold",
                        size=6,
                        color='#333333',
                        leading=7,
                        alignment=TA_RIGHT),
                     P(text=f"avg {data2:.2f}",
                        font="Roboto_Condensed-Regular",
                        size=6,
                        leading=7,
                        color='#999999',
                        alignment=TA_RIGHT),
                    P(text=f"{data3}%",
                        font="Roboto_Condensed-Regular",
                        size=6,
                        leading=7,
                        color='#999999',
                        alignment=TA_RIGHT)                           
                   ]]
    table = Table(table_data, colWidths=[cw * 0.6, cw * 0.15, cw * 0.15, cw * 0.1], rowHeights=rh)
    table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_SECTION),            
            ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_HEADER_TEXT),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
    return table

def create_barchart(styles, chart_params: ChartParams = None) -> Table:

    col_width  = chart_params.outer_table_size    
    row_height = 10

    title = P(chart_params.title, font="Roboto_Condensed-Bold", color="#4B6EA2", alignment=TA_CENTER)

    barchart_data = [[title]]
    rh = [row_height * 3]
    current_group = None
    for key in chart_params.values:
        group = chart_params.values[key].group
        if group is not None:
            if current_group is None or group != current_group:
                current_group = group
                sd = section_data(group, col_width * 0.95, row_height)
                barchart_data.append([sd])        
                rh.append(row_height)

        td = text_data(key, chart_params.values[key], col_width * 0.95, row_height)
        barchart_data.append([td])        
        rh.append(row_height)
        bd = bar_data(key, chart_params.values[key], col_width * 0.95, row_height/3)
        barchart_data.append([bd])
        rh.append(row_height/2)
    
    barchart_data.append([""])        
    rh.append(row_height)

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
