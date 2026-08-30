"""
Professional report definitions: fonts, colors, styles, and dataclasses.

Centralized configuration for all report styling and typography.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, Paragraph


@dataclass
class teamKPI:
    """Statistical values for a single radar metric."""
    name: str
    short_name: str    
    long_name: str
    group: str
    description: str
    unit: str
    value: float
    reverse: bool       
     

@dataclass
class ChartValue:
    """Statistical values for a single radar metric."""
    chart_val: float
    avg_val: float
    max_val: float
    min_val: float    
    percentile: float
    percentile_total: int
    group: str = None
    reverse: int = 0
    std_dev: float = None


@dataclass
class ChartParams:
    """Parameters for radar chart rendering."""
    chart_type: str
    outer_table_size: float    
    outer_table_bg_color: str
    outer_table_border_color: str    
    title: str    
    values: Dict[str, ChartValue] = field(default_factory=dict)


class ProgressBar(Flowable):
    def __init__(
        self,
        width,
        percentage,
        height=12,
        fill_color=colors.blue,
        background_color=colors.lightgrey,
        average_percentage=None,
        reverse=None
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.percentage = max(0, min(100, percentage))
        self.fill_color = fill_color        
        self.background_color = background_color        
        if reverse is not None:
            if reverse == 1:
                self.background_color = "#b5b3b3"
        self.average_percentage = max(0, min(100, average_percentage)) if average_percentage is not None else None

    def draw(self):
        r = self.height / 2

        # Background
        self.canv.setFillColor(self.background_color)
        self.canv.roundRect(
            0, 0, self.width, self.height, r,
            stroke=0, fill=1
        )

        # Filled portion
        filled_width = self.width * self.percentage / 100

        if filled_width > 0:
            self.canv.setFillColor(self.fill_color)

            # For very small percentages, avoid an oversized radius
            radius = min(r, filled_width / 2)

            self.canv.roundRect(
                0, 0, filled_width, self.height, radius,
                stroke=0, fill=1
            )

        # Average marker (thin vertical line)
        if self.average_percentage is not None:
            avg_x = self.width * self.average_percentage / 100
            self.canv.setStrokeColor(colors.HexColor("#555555"))
            self.canv.setLineWidth(1)
            self.canv.line(avg_x, 0, avg_x, self.height)
# ═════════════════════════════════════════════════════════════════════════
# FONT SETUP
# ═════════════════════════════════════════════════════════════════════════
def get_values(stats, team: str = None) -> Dict:
    v = {}
    v["team"] = team



    # Get team stats from list
    team_stats = next((s for s in stats if s.get('team') == team), None)

    # Find total n_events and n_matches from all teams in stats list
    total_n_events = sum(s.get('n_events', 0) for s in stats) if stats else 0
    total_n_matches = sum(s.get('n_matches', 0) for s in stats) if stats else 0
    v["n_events"] = total_n_events
    v["n_matches"] = total_n_matches

    if team_stats:
        v["n_events"] = team_stats.get('n_events')
        v["n_matches"] = team_stats.get('n_matches')
        v["n_metrics"] = team_stats.get('n_metrics')
        v["total_n_matches"] = total_n_matches
        v["total_n_events"] = total_n_events
    else:
        v["n_events"] = None
        v["n_matches"] = None
        v["n_metrics"] = None


    return  v

def get_color(values: ChartValue) -> colors.Color:
    percentile = values.percentile    
    total = values.percentile_total
    ratio = percentile / total
    if values.reverse == 1:
            ratio = 1 - ratio

    if ratio < 0.2:
        return colors.HexColor("#e90c0c")
    if ratio < 0.4:
        return colors.HexColor("#e96c0c")
    if ratio < 0.6:
            return colors.HexColor("#536fe0")
    if ratio < 0.8:
        return colors.HexColor("#4c9510")

    return colors.HexColor("#D619C3")

def register_custom_fonts():
    """Register available custom fonts from fonts/ and fonts/roboto/ directories."""
    fonts_dir = Path(__file__).parent.parent / "fonts"

    registered = {}

    # Dynamically discover and register all TTF fonts in the fonts directory and subdirectories
    if fonts_dir.exists():
        # Register fonts from main fonts directory
        for ttf_file in sorted(fonts_dir.glob("*.ttf")):
            font_name = ttf_file.stem
            try:
                pdfmetrics.registerFont(TTFont(font_name, str(ttf_file)))
                registered[font_name] = True
            except Exception as e:
                registered[font_name] = False

        # Register fonts from fonts/Roboto/ subdirectory
        roboto_dir = fonts_dir / "Roboto"
        if roboto_dir.exists():
            for ttf_file in sorted(roboto_dir.glob("*.ttf")):
                font_name = ttf_file.stem
                try:
                    pdfmetrics.registerFont(TTFont(font_name, str(ttf_file)))
                    registered[font_name] = True
                except Exception as e:
                    registered[font_name] = False

    return registered


# Register fonts on module load
_REGISTERED_FONTS = register_custom_fonts()

# Font name constants (with smart fallbacks)
FONT_HEADER = "BarlowCondensed-Bold"
FONT_HEADER = "Roboto_Condensed-Thin"
FONT_HEADER_REGULAR = "BarlowCondensed-Regular"
FONT_BODY = "BarlowCondensed-Regular"
FONT_BODY_EMPHASIS = "Inter-Medium"
FONT_BODY_BOLD = "Inter-SemiBold"


# ═════════════════════════════════════════════════════════════════════════
# COLOR PALETTE (Print-optimised)
# ═════════════════════════════════════════════════════════════════════════

# Neutrals
COLOR_BG_PAGE = colors.HexColor("#FFFFFF")          # Page background
COLOR_BG_SECTION = colors.HexColor("#F4F6FA")       # Card/section background
COLOR_BG_SECONDARY = colors.HexColor("#EAEdf5")     # Secondary surface
COLOR_TEXT_BODY = colors.HexColor("#12151A")        # Body text (near-black)
COLOR_TEXT_BODY_LIGHTER = colors.HexColor("#666666")        # Body text lighter
COLOR_TEXT_MUTED = colors.HexColor("#7A8299")       # Muted text
COLOR_BORDER_LIGHT = colors.HexColor("#D8DCE6")     # Light border
COLOR_BORDER_STRONG = colors.HexColor("#B8BFCC")    # Strong border

# Semantic: Teal (your team, positive)
COLOR_TEAL_PRIMARY = colors.HexColor("#007A6A")     # Forest Teal
COLOR_TEAL_TINT = colors.HexColor("#E6F4F1")        # Light teal background
COLOR_TEAL_MID = colors.HexColor("#B2D9D3")         # Mid teal

# Semantic: Amber (opposition, threat)
COLOR_AMBER_PRIMARY = colors.HexColor("#9A5F00")    # Dark Amber
COLOR_AMBER_TINT = colors.HexColor("#FDF3E0")       # Light amber background
COLOR_AMBER_MID = colors.HexColor("#F0C870")        # Mid amber

# Semantic: Red (priority/alert)
COLOR_RED_PRIMARY = colors.HexColor("#B52828")      # Deep Red
COLOR_RED_TINT = colors.HexColor("#FDEAEA")         # Light red background
COLOR_RED_MID = colors.HexColor("#FD9999")         # Light red background

# Header specific
COLOR_HEADER_BG = colors.HexColor("#12151A")        # Dark header background
COLOR_HEADER_TEXT = colors.white                    # White text in header


# ═════════════════════════════════════════════════════════════════════════
# KPI CONFIGURATION
# ═════════════════════════════════════════════════════════════════════════

# Key Performance Indicators for team analysis
team_kpis = []


# ═════════════════════════════════════════════════════════════════════════
# TYPOGRAPHY & STYLES
# ═════════════════════════════════════════════════════════════════════════

_STYLES_CACHE = None


# ═════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════

def letter_space(text: str, gap: float = 1) -> str:
    """Add letter spacing between characters while preserving original spaces."""
    spaces = " " * int(gap)
    result = []
    for i, char in enumerate(text):
        result.append(char)
        if i < len(text) - 1 and char != ' ' and text[i + 1] != ' ':
            result.append(spaces)
    return ''.join(result)

def P(text, font="Roboto-Regular", size=9, color="#333333",
      alignment=TA_LEFT, leading=None):

    return Paragraph(
        text,
        ParagraphStyle(
            "inline",
            fontName=font,
            fontSize=size,
            textColor=color,
            alignment=alignment,
            leading=leading or size * 1.45,
        )
    )

def get_styles():
    """Create custom professional report styles (cached)."""
    global _STYLES_CACHE

    if _STYLES_CACHE is not None:
        return _STYLES_CACHE

    styles = getSampleStyleSheet()

    def add_or_update_style(styles, style_obj):
        """Add style or update if it already exists."""
        try:
            styles.add(style_obj)
        except KeyError:
            pass

    # Page Title (38px, Barlow Condensed 800 equivalent)
    add_or_update_style(styles, ParagraphStyle(
        name='PageTitle',
        fontSize=38,
        fontName=FONT_HEADER,
        textColor=COLOR_HEADER_TEXT,
        alignment=TA_LEFT,
        spaceAfter=8,
        leading=38
    ))

    add_or_update_style(styles, ParagraphStyle(
        name='BigNumber',
        fontSize=26,
        fontName=FONT_HEADER,
        textColor=COLOR_TEXT_BODY,
        alignment=TA_LEFT,
        spaceAfter=8,
        leading=38
    ))

    # Section Label
    add_or_update_style(styles, ParagraphStyle(
        name='SectionLabel',
        fontSize=12,
        fontName=FONT_HEADER_REGULAR,
        textColor=COLOR_TEAL_PRIMARY,
        alignment=TA_LEFT,
        spaceAfter=10,
    ))

    add_or_update_style(styles, ParagraphStyle(
        name='SectionLabelTeal',
        fontSize=16,
        fontName=FONT_HEADER,
        textColor=COLOR_TEAL_PRIMARY,
        alignment=TA_LEFT,
        spaceAfter=10,
    ))

    add_or_update_style(styles, ParagraphStyle(
        name='SectionLabelAmber',
        fontSize=16,
        fontName=FONT_HEADER,
        textColor=COLOR_AMBER_PRIMARY,
        alignment=TA_LEFT,
        spaceAfter=10,
    ))

    add_or_update_style(styles, ParagraphStyle(
        name='SectionLabelRed',
        fontSize=16,
        fontName=FONT_HEADER,
        textColor=COLOR_RED_PRIMARY,
        alignment=TA_LEFT,
        spaceAfter=10,
    ))

    add_or_update_style(styles, ParagraphStyle(
        name='SectionLabelBlack',
        fontSize=16,
        fontName=FONT_HEADER,
        textColor=COLOR_TEXT_BODY_LIGHTER,
        alignment=TA_CENTER,
        spaceAfter=10,
    ))

    # Card Label
    add_or_update_style(styles, ParagraphStyle(
        name='CardLabel',
        fontSize=10,
        fontName=FONT_BODY_BOLD,
        textColor=COLOR_TEAL_PRIMARY,
        alignment=TA_CENTER,
    ))

    add_or_update_style(styles, ParagraphStyle(
        name='CardLabelTeal',
        fontSize=10,
        fontName=FONT_HEADER,
        textColor=COLOR_TEAL_PRIMARY,
        alignment=TA_LEFT,
    ))
    add_or_update_style(styles, ParagraphStyle(
            name='CardLabelAmber',
            fontSize=10,
            fontName=FONT_HEADER,
            textColor=COLOR_AMBER_PRIMARY,
            alignment=TA_LEFT,
    ))

    add_or_update_style(styles, ParagraphStyle(
                name='CardLabelRed',
                fontSize=10,
                fontName=FONT_HEADER,
                textColor=COLOR_RED_PRIMARY,
                alignment=TA_LEFT,
    ))

    add_or_update_style(styles, ParagraphStyle(
            name='CaptionTeal',
            fontSize=10,
            fontName=FONT_HEADER,
            textColor=COLOR_TEAL_MID,
            alignment=TA_CENTER,
        ))
    add_or_update_style(styles, ParagraphStyle(
            name='CaptionAmber',
            fontSize=10,
            fontName=FONT_HEADER,
            textColor=COLOR_AMBER_MID,
            alignment=TA_CENTER,
    ))

    add_or_update_style(styles, ParagraphStyle(
            name='CaptionRed',
            fontSize=10,
            fontName=FONT_HEADER,
            textColor=COLOR_RED_MID,
            alignment=TA_CENTER,
    ))

    add_or_update_style(styles, ParagraphStyle(
            name='CaptionGray',
            fontSize=10,
            fontName=FONT_HEADER,
            textColor=COLOR_TEXT_MUTED,
            alignment=TA_CENTER,
        ))

    add_or_update_style(styles, ParagraphStyle(
                name='tableNumber',
                fontSize=10,
                fontName=FONT_HEADER,
                textColor=COLOR_TEXT_BODY,
                alignment=TA_RIGHT
            ))
    add_or_update_style(styles, ParagraphStyle(
                    name='score',
                    fontSize=9,
                    fontName=FONT_HEADER,
                    textColor=COLOR_TEXT_BODY,
                    alignment=TA_CENTER
                ))
    add_or_update_style(styles, ParagraphStyle(
                name='tableText',
                fontSize=8,
                fontName=FONT_BODY,
                textColor=COLOR_TEXT_BODY,
                alignment=TA_RIGHT                
            ))
    add_or_update_style(styles, ParagraphStyle(
                    name='tableTextRight',
                    fontSize=8,
                    fontName=FONT_BODY,
                    textColor=COLOR_TEXT_BODY,
                    alignment=TA_RIGHT
                ))
    add_or_update_style(styles, ParagraphStyle(
                        name='tableTextLeft',
                        fontSize=8,
                        fontName=FONT_BODY,
                        textColor=COLOR_TEXT_BODY,
                        alignment=TA_LEFT
                    ))
    add_or_update_style(styles, ParagraphStyle(
                        name='tableTextCenter',
                        fontSize=8,
                        fontName=FONT_BODY,
                        textColor=COLOR_TEXT_BODY,
                        alignment=TA_CENTER
                    ))                
    add_or_update_style(styles, ParagraphStyle(
                    name='chartTitle',
                    fontSize=8,
                    fontName=FONT_HEADER,
                    textColor=COLOR_TEXT_BODY_LIGHTER,
                    alignment=TA_LEFT                
                ))
    add_or_update_style(styles, ParagraphStyle(
                        name='chartTitleCenter',
                        fontSize=8,
                        fontName=FONT_HEADER,
                        textColor=colors.HexColor("#8A8989"),
                        alignment=TA_CENTER                
                    ))
    add_or_update_style(styles, ParagraphStyle(
                            name='chartBottom',
                            fontSize=6,
                            fontName=FONT_BODY,
                            textColor=colors.HexColor("#323131"),
                            alignment=TA_CENTER                
                        ))
    # Body Text
    add_or_update_style(styles, ParagraphStyle(
        name='BodyText',
        fontSize=11,
        fontName=FONT_BODY,
        textColor=COLOR_TEXT_BODY,
        alignment=TA_LEFT,
        spaceAfter=12,
        leading=17
    ))

    # Stat Value
    add_or_update_style(styles, ParagraphStyle(
        name='StatValue',
        fontSize=20,
        fontName=FONT_BODY_BOLD,
        textColor=COLOR_TEXT_BODY,
        alignment=TA_CENTER,
        leading=20
    ))

    # Hero Number
    add_or_update_style(styles, ParagraphStyle(
        name='HeroNumber',
        fontSize=36,
        fontName=FONT_HEADER,
        textColor=COLOR_TEAL_PRIMARY,
        alignment=TA_CENTER,
        leading=36
    ))

    # Meta text
    add_or_update_style(styles, ParagraphStyle(
        name='MetaText',
        fontSize=11,
        fontName=FONT_BODY,
        textColor=COLOR_TEXT_MUTED,
        alignment=TA_LEFT,
        spaceAfter=4
    ))

    # Small label
    add_or_update_style(styles, ParagraphStyle(
        name='SmallLabel',
        fontSize=9,
        fontName=FONT_BODY_BOLD,
        textColor=COLOR_TEXT_MUTED,
        alignment=TA_LEFT,
    ))

    _STYLES_CACHE = styles
    return styles
