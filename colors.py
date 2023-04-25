"""message formatting module"""
import re

STRIP_REGEX = re.compile(
    "\x1f|\x02|\x12|\x0f|\x16|\x03(?:\d{1,2}(?:,\d{1,2})?)?",
    re.UNICODE
)

WHITE = '00'
BLACK = '01'
BLUE = '02'
GREEN = '03'
RED = '04'
BROWN = '05'
PURPLE = '06'
ORANGE = '07'
YELLOW = '08'
LIME = '09'
TEAL = '10'
CYAN = '11'
LIGHT_BLUE = '12'
PINK = '13'
GREY = '14'
SILVER = '15'

# SPECIAL
BLUE_TWITTER = '47'

CONTROL_COLOR = '\x03'
BOLD = '\x02'
UNDERLINE = '\x1F'
ITALIC = '\x1D'


def colorize(text, fg, bg=None):
    """Colorizes text

    :param str text: text to colorize
    :param str fg: foreground color code (see colors above)
    :param str|None bg: background color code (see colors above)

    :returns: colorized text
    :rtype: str
    """
    if not bg:
        return f'{CONTROL_COLOR}{fg}{text}{CONTROL_COLOR}'
    else:
        return f'{CONTROL_COLOR}{fg},{bg}{text}{CONTROL_COLOR}'


def strip_formatting(message):
    """Returns message stripped of all formatting"""
    return STRIP_REGEX.sub(message, '')
