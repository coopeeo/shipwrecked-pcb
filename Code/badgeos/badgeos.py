import _thread
import asyncio

from badgeos.hardware.display import BadgeDisplay
from badgeos.hardware.radio import BadgeRadio

from badgeos.contacts import ContactsManager
from badgeos.notifs import NotifManager
from badgeos.apps import AppManager

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
        # 2. Start the app thread.
        # 3. Schedule the needed background tasks.
        # 4. Start the asyncio event loop.

        # Step 1:
        # Things to initialize:
        # - Hardware: Display, button hardware, radio hardware
        # - IRQs: Button press, button release, radio receive
        # - Software: Contacts manager, notification manager

        # Step 2:
        _thread.start_new_thread(self.app_thread, ())

        # Step 3:
        # background tasks to schedule:
        # idk yet, maybe radio stuff?

        # Step 4:

    def app_thread(self):
        # TODO
        pass