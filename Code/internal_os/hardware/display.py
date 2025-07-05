from machine import Pin, SPI, Timer
from internal_os.hardware.einkdriver import EPD

class BadgeDisplay:
    """
    Manages the display. 
    TODO: make this and einkdriver async
    TODO: add partial refresh support
    """
    def __init__(self):
        # initialize rp2040 peripherals
        self.spi = SPI(0, baudrate=1_000_000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(20))
        self.cs = Pin(24, Pin.OUT)
        self.dc = Pin(25, Pin.OUT)
        self.rst = Pin(26, Pin.OUT)
        self.busy = Pin(27, Pin.IN)

        self.display = EPD(self.spi, self.cs, self.dc, self.rst, self.busy)
        self.display.init()
        self.display.sleep()

        self.idle_timer = Timer(-1)
    
    def reset_idle_timer(self):
        """Reset the idle timer to prevent the display from sleeping for another 5 seconds"""
        self.idle_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=lambda _: self.sleep())

    def sleep(self):
        """Put the display to sleep to save power"""
        self.display.sleep()
    
    def fill(self, color):
        """Fill the entire buffer with a color (0=black, 1=white)"""
        self.reset_idle_timer()
        self.display.fill(color)
    
    def pixel(self, x, y, color):
        """Set a pixel color (0=black, 1=white)"""
        self.reset_idle_timer()
        self.display.pixel(x, y, color)
    
    def hline(self, x, y, w, color):
        """Draw a horizontal line"""
        self.reset_idle_timer()
        self.display.hline(x, y, w, color)
    
    def vline(self, x, y, h, color):
        """Draw a vertical line"""
        self.reset_idle_timer()
        self.display.vline(x, y, h, color)
    
    def line(self, x1, y1, x2, y2, color):
        """Draw a line"""
        self.reset_idle_timer()
        self.display.line(x1, y1, x2, y2, color)
    
    def rect(self, x, y, w, h, color):
        """Draw a rectangle"""
        self.reset_idle_timer()
        self.display.rect(x, y, w, h, color)
    
    def fill_rect(self, x, y, w, h, color):
        """Draw a filled rectangle"""
        self.reset_idle_timer()
        self.display.fill_rect(x, y, w, h, color)
    
    def text(self, text, x, y, color=0):
        """Draw text"""
        self.reset_idle_timer()
        self.display.text(text, x, y, color)