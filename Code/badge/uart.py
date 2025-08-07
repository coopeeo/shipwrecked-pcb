#from internal_os.internalos import BadgeUART
from internal_os.internalos import InternalOS
internal_os = InternalOS.instance()

def present() -> bool:
    """
    Check if the UART is present.
    :return: True if the UART is present, False otherwise.
    """
    return True