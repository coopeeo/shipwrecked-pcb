try:
    from typing import List, TypeAlias
except ImportError:
    # we're on an MCU, typing is not available
    pass

import logging
logger = logging.getLogger("Buttons")

from internal_os.internalos import InternalOS

internal_os = InternalOS.instance()

Button: TypeAlias = int
class Buttons:
    """
    An enum of all the available buttons.
    The buttons are numbered clockwise.
    Example: DEG0 is the button in the right, DEG225 is the button in the bottom left.
    """
    DEG0: Button = 3
    DEG22_5: Button = 10
    DEG45: Button = 4
    DEG67_5: Button = 13
    DEG90: Button = 5
    DEG112_5: Button = 12
    DEG135: Button = 6
    DEG157_5: Button = 15
    DEG180: Button = 7
    DEG202_5: Button = 14
    DEG225: Button = 0
    DEG247_5: Button = 9
    DEG270: Button = 1
    DEG292_5: Button = 8
    DEG315: Button = 2
    DEG337_5: Button = 11



def get_button(button: Button) -> bool:
    """
    Get the state of a button.
    :param button: The button to check.
    :return: True if the button is pressed, False otherwise.
    """
    if button == 0:
        logger.warning("Button 0 is the home button. Your application cannot access it. If you want to detect yourself being closed, implement the on_close function.")
    return internal_os.buttons.is_pressed(button)