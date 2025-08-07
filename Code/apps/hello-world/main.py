import badge
import utime
from badge.radio import Packet

class App(badge.BaseApp):
    def on_open(self) -> None:
        self.logger.info("Hello World App is now open!")
        self.counter = 0
        badge.display.fill(1)  # Clear the display
        badge.display.text("Hello World!", 0, 0, 0)  # Display "Hello World!" at the top left
        badge.display.show()  # Show the updated display
    def loop(self) -> None:
        self.logger.info(f"Hello World! Counter: {self.counter}, button pressed: {badge.input.get_button(1)}")
        self.counter += 1
        if badge.input.get_button(1):  # If button 1 is pressed
            badge.display.text(f"Counter is {self.counter}", 0, 10, 0)
            badge.display.show()  # Update the display with the new counter value
            badge.radio.send_packet(0xffff, f"Hello World! \n Here is some long text that is likely to get corrupted :( Counter: {self.counter}".encode('utf-8'))  # Send a packet with the counter value
        utime.sleep(1)
    def on_packet(self, packet: Packet, in_foreground: bool) -> None:
        self.logger.info(f"Received packet: {packet}")
        if in_foreground:
            badge.display.text(packet.data.decode('utf-8'), 0, 20, 0)