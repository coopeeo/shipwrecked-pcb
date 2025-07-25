import badge
import utime

# NOTE: MOST APPS SHOULD NOT NEED THESE IMPORTS.
# home-screen is messing with app launches, so it's special.
# Please especially note that asyncio is not likely to work for
# normal apps - it _will_ interfere with the main OS's event loop
import asyncio
from internal_os.internalos import InternalOS
internal_os = InternalOS.instance()

class App(badge.BaseApp):
    def on_open(self) -> None:
        self.logger.info("Home screen opening...")
        # TODO: do display stuff, etc.
    def loop(self) -> None:
        if badge.input.get_button(1):
            # TODO: launch apps more cleverer
            hello_world_app = internal_os.apps.get_app_by_path('/apps/hello-world')
            if not hello_world_app:
                self.logger.error("Hello World app not found. Cannot launch test app.")
                return
            self.launch_app(hello_world_app)
    def launch_app(self, app_repr) -> None:
        """
        Launch the specified app.
        :param app_repr: The AppRepr instance representing the app to launch.
        """
        self.logger.info(f"Launching app: {app_repr.display_name}")
        asyncio.create_task(internal_os.apps.launch_app(app_repr))
        while internal_os.apps.fg_app_running:
            utime.sleep(0.1)  # Wait for the app machinery to tell us to stop
