import badge
import utime

class App(badge.BaseApp):
    def on_open(self) -> None:
        self.logger.info("Hello World App is now open!")
        self.counter = 0
    def loop(self) -> None:
        self.logger.info(f"Hello World! Counter: {self.counter}, button pressed: {badge.input.get_button(1)}")
        self.counter += 1
        utime.sleep(1)