import badge
import utime
from machine import unique_id

class App(badge.BaseApp):
    def __init__(self) -> None:
        self.last_button = False
        self.received_packet = None
    def on_open(self) -> None:
        badge.display.fill(1)
        badge.display.text("messaging testing app 3000", 0, 0, 0)
        badge.display.show()
    def loop(self) -> None:
        if badge.input.get_button(1):
            if not self.last_button:
                badge.radio.send_packet(0x4f53, b"testing 1234")
            self.last_button = True
        else:
            self.last_button = False
        
        if self.received_packet:
            self.logger.info(f"Received packet: {self.received_packet}")
            badge.display.fill(1)
            badge.display.nice_text(f"Received:\n{self.received_packet.data.decode()}", 0, 0)
            badge.display.show()
            self.received_packet = None
    
    def on_packet(self, packet: badge.radio.Packet, is_foreground: bool) -> None:
        if not is_foreground:
            # TODO: send notif
            self.logger.info(f"Received packet in background app: {packet}")
        else:
            self.logger.info(f"Received packet in foreground app: {packet}")
            self.received_packet = packet