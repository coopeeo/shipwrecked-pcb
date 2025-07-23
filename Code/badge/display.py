try:
    from typing import List
except ImportError:
    # we're on an MCU, typing is not available
    pass

import _thread

def _is_display_allowed() -> bool:
    """
    Check if the display is allowed to be used.
    """
    # thread ident 2 = core 1 = foregrounded app
    # we can only rely on this because of the RP2040's implementation of get_ident():
    # https://github.com/micropython/micropython/blob/master/ports/rp2/mpthreadport.c#L123
    return _thread.get_ident() == 2  

from internal_os.internalos import InternalOS

internal_os = InternalOS.instance()

def sleep():
    """
    Put the display to sleep to save power.
    User code rarely has to call this, it's handled internally most of the time.
    """
    if not _is_display_allowed():
        raise RuntimeError("Cannot call display functions from a backgrounded app context.")
    internal_os.display.sleep()

def show() -> None:
    """
    Push the contents of the internal framebuffer to the display.
    This does a full refresh of the E-Ink (takes a few seconds).
    NOTE: YOUR DRAWING WILL NOT DO ANYTHING UNTIL YOU CALL THIS FUNCTION!
    """
    if not _is_display_allowed():
        raise RuntimeError("Cannot call display functions from a backgrounded app context.")
    internal_os.display.show()

def fill(color: int) -> None:
    """
    Fill the entire display with a color.
    :param color: Color to fill (0=black, 1=white).
    """
    if not _is_display_allowed():
        raise RuntimeError("Cannot call display functions from a backgrounded app context.")
    internal_os.display.fill(color)

def pixel(x: int, y: int, color: int) -> None:
    """
    Set a pixel color.
    :param x: X coordinate of the pixel.
    :param y: Y coordinate of the pixel.
    :param color: Color of the pixel (0=black, 1=white).
    """
    if not _is_display_allowed():
        raise RuntimeError("Cannot call display functions from a backgrounded app context.")
    internal_os.display.pixel(x, y, color)

def hline(x: int, y: int, w: int, color: int) -> None:
    """
    Draw a horizontal line.
    :param x: X coordinate of the start of the line.
    :param y: Y coordinate of the line.
    :param w: Width of the line.
    :param color: Color of the line (0=black, 1=white).
    """
    if not _is_display_allowed():
        raise RuntimeError("Cannot call display functions from a backgrounded app context.")
    internal_os.display.hline(x, y, w, color)

def vline(x: int, y: int, h: int, color: int) -> None:
    """
    Draw a vertical line.
    :param x: X coordinate of the line.
    :param y: Y coordinate of the start of the line.
    :param h: Height of the line.
    :param color: Color of the line (0=black, 1=white).
    """
    if not _is_display_allowed():
        raise RuntimeError("Cannot call display functions from a backgrounded app context.")
    internal_os.display.vline(x, y, h, color)

def line(x1: int, y1: int, x2: int, y2: int, color: int) -> None:
    """
    Draw a line.
    :param x1: X coordinate of the start of the line.
    :param y1: Y coordinate of the start of the line.
    :param x2: X coordinate of the end of the line.
    :param y2: Y coordinate of the end of the line.
    :param color: Color of the line (0=black, 1=white).
    """
    if not _is_display_allowed():
        raise RuntimeError("Cannot call display functions from a backgrounded app context.")
    internal_os.display.line(x1, y1, x2, y2, color)

def rect(x: int, y: int, w: int, h: int, color: int) -> None:
    """
    Draw a rectangle (stroke only).
    :param x: X coordinate of the top-left corner.
    :param y: Y coordinate of the top-left corner.
    :param w: Width of the rectangle.
    :param h: Height of the rectangle.
    :param color: Color of the rectangle (0=black, 1=white).
    """
    if not _is_display_allowed():
        raise RuntimeError("Cannot call display functions from a backgrounded app context.")
    internal_os.display.rect(x, y, w, h, color)

def fill_rect(x: int, y: int, w: int, h: int, color: int) -> None:
    """
    Draw a filled rectangle.
    :param x: X coordinate of the top-left corner.
    :param y: Y coordinate of the top-left corner.
    :param w: Width of the rectangle.
    :param h: Height of the rectangle.
    :param color: Color of the rectangle (0=black, 1=white).
    """
    if not _is_display_allowed():
        raise RuntimeError("Cannot call display functions from a backgrounded app context.")
    internal_os.display.fill_rect(x, y, w, h, color)

def text(text: str, x: int, y: int, color: int = 0) -> None:
    """
    Draw text on the display.
    :param text: The text to draw.
    :param x: X coordinate of the text.
    :param y: Y coordinate of the text.
    :param color: Color of the text (0=black, 1=white).
    """
    if not _is_display_allowed():
        raise RuntimeError("Cannot call display functions from a backgrounded app context.")
    internal_os.display.text(text, x, y, color)