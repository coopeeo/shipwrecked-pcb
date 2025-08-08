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
        """ self.logger.info(f"Hello World! Counter: {self.counter}, button pressed: {badge.input.get_button(1)}")
        self.counter += 1
        badge.utils.set_led(self.counter % 2 == 0)  # Toggle LED every second loop
        utime.sleep(1) """
        for i in range(0, 65536, 500):
            badge.utils.set_led_pwm(i)
            utime.sleep(0.001)
        for i in range(65535, 0, -500):
            badge.utils.set_led_pwm(i)
            utime.sleep(0.001)
    def on_packet(self, packet: Packet, in_foreground: bool) -> None:
        self.logger.info(f"Received packet: {packet}")
        if in_foreground:
            badge.display.text(packet.data.decode('utf-8'), 0, 20, 0)