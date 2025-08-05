import badge
import utime
from machine import unique_id

class App(badge.BaseApp):
    def on_open(self) -> None:
        badge.display.fill(1)
        badge.display.text("messaging testing app 3000", 0, 0, 0)
        badge.display.show()
    def loop(self) -> None:
        badge.radio.send_packet(badge.radio.Packet(
            dest=int(0x04f5).to_bytes(2),
            app_number=int(1).to_bytes(2),
            data=b"testing 123"
        ))
        utime.sleep(1)