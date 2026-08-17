"""
Professional report definitions: fonts, colors, and styles.

Centralized configuration for all report styling and typography.
"""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ═════════════════════════════════════════════════════════════════════════
# FONT SETUP
# ═════════════════════════════════════════════════════════════════════════

def register_custom_fonts():
    """Register available custom fonts from fonts/ directory."""
    fonts_dir = Path(__file__).parent.parent / "fonts"

    fonts_to_register = {
        "BarlowCondensed-Regular": "BarlowCondensed-Regular.ttf",
        "BarlowCondensed-Bold": "BarlowCondensed-Bold.ttf",
        "Inter-Regular": "Inter-Regular.ttf",      # Weight 400
        "Inter-Medium": "Inter-Medium.ttf",        # Weight 500
        "Inter-SemiBold": "Inter-SemiBold.ttf",    # Weight 600
    }

    registered = {}
    for font_name, filename in fonts_to_register.items():
        filepath = fonts_dir / filename
        if filepath.exists():
            try:
                pdfmetrics.registerFont(TTFont(font_name, str(filepath)))
                registered[font_name] = True
            except Exception as e:
                registered[font_name] = False
        else:
            registered[font_name] = False

    return registered


# Register fonts on module load
_REGISTERED_FONTS = register_custom_fonts()

# Font name constants (with smart fallbacks)
FONT_HEADER = "BarlowCondensed-Bold" if _REGISTERED_FONTS.get("BarlowCondensed-Bold") else "Helvetica-Bold"
FONT_HEADER_REGULAR = "BarlowCondensed-Regular" if _REGISTERED_FONTS.get("BarlowCondensed-Regular") else "Helvetica"
FONT_BODY = "Inter-Regular" if _REGISTERED_FONTS.get("Inter-Regular") else "Helvetica"
FONT_BODY_EMPHASIS = "Inter-Medium" if _REGISTERED_FONTS.get("Inter-Medium") else "Helvetica-Bold"
FONT_BODY_BOLD = "Inter-SemiBold" if _REGISTERED_FONTS.get("Inter-SemiBold") else "Helvetica-Bold"


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

# Header specific
COLOR_HEADER_BG = colors.HexColor("#12151A")        # Dark header background
COLOR_HEADER_TEXT = colors.white                    # White text in header


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
