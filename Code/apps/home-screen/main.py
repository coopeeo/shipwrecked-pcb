import badge
import utime

# NOTE: MOST APPS RFC2119-SHOULD-NOT NEED THESE IMPORTS.
# home-screen is messing with app launches, so it's special.
# Please especially note that asyncio is not likely to work for
# normal apps - it _will_ interfere with the main OS's event loop
import asyncio
from internal_os.internalos import InternalOS
internal_os = InternalOS.instance()

class App(badge.BaseApp):
    def __init__(self):
        self.cursor_pos = 0
        self.old_button = False
        self.button_time = utime.ticks_ms()

    def on_open(self) -> None:
        self.logger.info("Home screen opening...")
        self.cursor_pos = 0
        self.render_home_screen()

    def loop(self) -> None:
        if badge.input.get_button(badge.input.Buttons.SW11):
            self.old_button = True
        else:
            if self.old_button:
                # just released
                self.logger.info("Button 8 pressed")
                self.cursor_pos = (self.cursor_pos - 1) % len(internal_os.apps.registered_apps)
                self.render_home_screen()
            self.old_button = False

        if badge.input.get_button(badge.input.Buttons.SW4):
            self.old_button = True
        else:
            if self.old_button:
                # just released
                self.logger.info("Button 1 pressed")
                self.cursor_pos = (self.cursor_pos + 1) % len(internal_os.apps.registered_apps)
                self.render_home_screen()
            self.old_button = False

        if badge.input.get_button(badge.input.Buttons.SW12):
            self.old_button = True
        else:
            if self.old_button:
                # just released
                self.logger.info("Button 9 pressed")
                self.logger.info(f"Launching app at position {self.cursor_pos}")
                self.launch_app(internal_os.apps.registered_apps[self.cursor_pos])
                return # don't run the rest of the loop - return control to the OS
            self.old_button = False

    def render_home_screen(self):
        """Render the home screen display."""
        badge.display.fill(1)
        for i, app in enumerate(internal_os.apps.registered_apps):
            current_screen = self.cursor_pos // 6
            if i < current_screen * 6 or i >= (current_screen + 1) * 6:
                continue
            app_x = (i % 3) * 66
            app_y = (i // 3) * 58 + 11
            self.draw_app_icon(app, app_x, app_y, self.cursor_pos == i)
        badge.display.show()

    def draw_app_icon(self, app_repr, x, y, selected):
        fb = badge.display.import_pbm(app_repr.logo_path)
        badge.display.blit(fb, x+9, y)
        if selected:
            badge.display.rect(x+7, y-2, 52, 52, 0)
        for i, frag in enumerate([app_repr.display_name[j:j+7] for j in range(0, len(app_repr.display_name), 7)]):
            badge.display.text(frag, x+5, y+50+i*9, 0)

    def launch_app(self, app_repr) -> None:
        """
        Launch the specified app.
        :param app_repr: The AppRepr instance representing the app to launch.
        """
        self.logger.info(f"Launching app: {app_repr.display_name}")
        asyncio.create_task(internal_os.apps.launch_app(app_repr))
        while internal_os.apps.fg_app_running:
            utime.sleep(0.1)  # Wait for the app machinery to tell us to stop
