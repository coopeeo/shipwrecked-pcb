import _thread
import asyncio

from badgeos.hardware.display import BadgeDisplay
from badgeos.hardware.buttons import BadgeButtons
from badgeos.hardware.radio import BadgeRadio

from badgeos.contacts import ContactsManager
from badgeos.notifs import NotifManager
from badgeos.apps import AppManager

# enable error reports for errors in ISRs
import micropython
micropython.alloc_emergency_exception_buf(100)

class BadgeOS:
    """
    The class that manages the badge. It runs across two cores. The main core manages background tasks and runs with asyncio. The second core runs the app thread (synchronously).
    To start the badge, initialize the class, then call badge.start().
    """
    def __init__(self):
        pass
    
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

        # software
        self.contacts = ContactsManager()
        self.notifs = NotifManager()
        self.apps = AppManager()


        # Step 3:
        asyncio.create_task(self.apps.scan_forever())

        # Step 4:
        asyncio.run(self.run_async())

    async def run_async(self):
        """
        The main async loop for the badge. This runs on the main core.
        """
        while True:
            await asyncio.sleep(1)