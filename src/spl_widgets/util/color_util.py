from openpyxl.cell.rich_text import TextBlock, CellRichText
from openpyxl.cell.text import InlineFont
import re

# This regex is largely simplified now & does not use exact ANSI escape codes
# because there is literally no reason to, these will never be printed to terminal 

# instead, I use an abbreviated version: \Rabc\C is a red "abc" instead of \x1b[31mabc\x1b[39m
# because isn't that just so much better

# to get a sense for this working use https://regex101.com/r/B0LoLF/1
COLOR_TEXT_RE = r"(?:\\([RGY]))?([^\\]+)(?:\\C)?"

# colors are ARGB, so first 2 are alpha channel
RED = InlineFont(color="009F2B00")
GREEN = InlineFont(color="0004BD04")
YELLOW = InlineFont(color="00D37506")

font_colors = {
    "R": RED,
    "G": GREEN,
    "Y": YELLOW
    # "C" token is CLEARSTYLE, but that doesn't get a font
}

def to_rich_text(in_text) -> CellRichText:
    matches: list[tuple[str,str]] = re.findall(COLOR_TEXT_RE, in_text)
    text = CellRichText()

    for (color, char) in matches:
        if color == '':
            text.append(char)
        else:
            text.append(
                TextBlock(font_colors[color], char)
            )

    return text

