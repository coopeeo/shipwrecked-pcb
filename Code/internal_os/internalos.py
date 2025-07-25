import _thread
import asyncio

from machine import RTC, Pin, PWM, unique_id

from internal_os.hardware.display import BadgeDisplay
from internal_os.hardware.buttons import BadgeButtons
from internal_os.hardware.radio import BadgeRadio

from internal_os.contacts import ContactsManager
from internal_os.notifs import NotifManager
from internal_os.apps import AppManager

# enable error reports for errors in ISRs
import micropython
micropython.alloc_emergency_exception_buf(100)

# XXX: temp function to launch a test app
# will be removed when the app manager is implemented
async def launch_test_app(manager: AppManager) -> None:
    """
    Launch a test app for debugging purposes.
    """
    await asyncio.sleep(3)
    hello_world_app = manager.get_app_by_path('/apps/hello-world')
    if not hello_world_app:
        manager.logger.error("Hello World app not found. Cannot launch test app.")
        return
    await manager.launch_app(hello_world_app)  # Launch the first registered app

class InternalOS:
    """
    The class that manages the badge. It runs across two cores. The main core manages background tasks and runs with asyncio. The second core runs the app thread (synchronously).
    To start the badge, initialize the class, then call badge.start().
    To allow access from various contexts, this class is a singleton.
    """
    
    @classmethod
    def instance(cls):
        """
        Returns the singleton instance of InternalOS.
        If it doesn't exist, creates a new one.
        """
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
    
    def start(self):
        """
        Starts the badge. Never returns.
        """
        # To do in this function:
        # 1. Initialize hardware, IRQs, state, etc.
        # 2. ~~Start the app thread.~~
        # 3. Schedule the needed background tasks.
        # 4. Start the asyncio event loop.

        # Step 1:
        # hardware
        self.display = BadgeDisplay()
        self.radio = BadgeRadio()
        self.buttons = BadgeButtons()
        self.rtc = RTC()
        self.buzzer = PWM(Pin(28, Pin.OUT))
        self.led = PWM(Pin(16, Pin.OUT))

        # software
        self.contacts = ContactsManager()
        self.notifs = NotifManager()
        self.apps = AppManager(self.buttons)


        # Step 3:
        asyncio.create_task(self.apps.scan_forever(interval=15)) # TODO: lower this interval in prod?
        asyncio.create_task(self.apps.home_button_watcher())
        asyncio.create_task(launch_test_app(self.apps)) # TODO: remove this when the app manager is implemented

        # Step 4:
        asyncio.run(self.run_async())

    async def run_async(self):
        """
        The main async loop for the badge. This runs on the main core.
        """
        while True:
            await asyncio.sleep(1)

        
    def get_badge_id(self) -> str:
        """
        Returns the badge ID as a hex string.
        The badge ID is the last 2 bytes (4 digits) of the machine.unique_id().
        """
        return unique_id().hex()[-4:]