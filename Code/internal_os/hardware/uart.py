from machine import I2C, Pin, UART
import logging
import asyncio

try:
    from typing import List
except ImportError:
    # we're on an MCU, typing is not available
    pass

class BadgeUART:
    def __init__(self) -> None:
        self.logger = logging.getLogger("BadgeUART")
        self.logger.setLevel(logging.DEBUG)
        self.uart_detect = Pin(3, Pin.IN, Pin.PULL_UP)
        self.uart = UART(1, baudrate=115200, tx=4, rx=5)

    def detect_badge(self) -> bool:
        """
        Check if the UART is present.
        :return: True if the UART is present, False otherwise.
        """
        try:
            return not self.uart_detect.value()  # active low
        except Exception as e:
            self.logger.error(f"Error checking UART presence: {e}")
            return False
        
    def try_connect(self) -> bool:
        """
        Attempt to connect to the UART.
        :return: True if connection is successful, False otherwise.
        """
        if self.detect_badge():
            self.logger.info("Badge UART detected. Attempting to connect...")
            # boop
            try:
                self.uart.init(bits=8, parity=None, stop=2)
                self.logger.info("Badge UART connection successful.")
            except Exception as e:
                self.logger.error(f"Failed to initialize UART: {e}")
                return False
            return True
        else:
            self.logger.warning("Badge UART not detected.")
            return False