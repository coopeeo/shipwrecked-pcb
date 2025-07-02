try:
    from typing import List, Optional, Dict
except ImportError:
    # we're on an MCU, typing is not available
    pass
import asyncio
import logging
import os
import json
import _thread
import utime

class AppRepr:
    """
    This class represents a single app that is known to the badge. It may or may not be instantiated.
    """
    app_path: str
    display_name: str
    logo_path: str
    full_screen: bool
    suppress_notifs: bool
    permissions: List[str]
    radio_settings: Dict
    app_number: str

    @classmethod
    def from_json(cls, path: str, json_str: str) -> 'AppRepr':
        """
        Create an AppRepr instance from a JSON representation.
        :param json_data: The manifest representing the app.
        :return: An instance of AppRepr.
        """
        json_data = json.loads(json_str)
        app_repr = cls()
        app_repr.app_path = path
        app_repr.display_name = json_data.get("display_name", "")
        app_repr.logo_path = json_data.get("logo_path", "")
        app_repr.full_screen = json_data.get("full_screen", False)
        app_repr.suppress_notifs = json_data.get("suppress_notifs", False)
        app_repr.permissions = json_data.get("permissions", [])
        app_repr.radio_settings = json_data.get("radio_settings", {})
        app_repr.app_number = json_data.get("app_number", "")
        return app_repr

async def acquire_lock(lock: _thread.LockType, timeout: Optional[float] = None):
    """
    Acquire a lock asynchronously with an optional timeout.
    :param lock: The lock to acquire.
    :param timeout: Optional timeout in seconds.
    :return: True if the lock was acquired, False if timed out.
    """
    aquired = False
    start_time = utime.ticks_ms()
    while not aquired:
        if lock.acquire(0): # 0 means non-blocking
            aquired = True
        else:
            if timeout is not None:
                elapsed = utime.ticks_diff(utime.ticks_ms(), start_time)
                if elapsed >= timeout * 1000:
                    raise TimeoutError(f"Failed to acquire lock within {timeout} seconds.")
            await asyncio.sleep(0.1)  # Yield control to the event loop

def app_thread(app_repr: AppRepr, manager: 'AppManager') -> None:
    """
    The thread that runs the app. It should run synchronously.
    :param app_repr: The AppRepr instance representing the app to run.
    :param manager: The AppManager instance managing the app.
    """
    # set up logging
    logger = logging.getLogger("App-" + app_repr.display_name)
    logger.info(f"Starting app: {app_repr.display_name} from {app_repr.app_path}")
    # Acquire the lock before running the app
    manager.app_lock.acquire(1) # 1 means block until we get it
    logger.debug(f"Acquired app lock")
    try:
        applib = __import__(app_repr.app_path + '.main', globals(), locals(), ['App'])
        logger.debug(f"Imported app module: {app_repr.app_path}.main")
        # check that the app has an App class, and that that class descends from BaseApp
        if not hasattr(applib, 'App'):
            raise ImportError(f"App {app_repr.display_name} does not define an 'App' class.")
        app_class = applib.App
        # TODO: build out the app API, then actually run the app here

    except Exception as e:
        logger.error(f"Error running app {app_repr.display_name}: {e}")
    finally:
        # Release the lock when done
        manager.app_lock.release()

class AppManager:
    """
    The AppManager class is responsible for managing the apps on the badge.
    It handles app registration, loading, and execution.
    """
    def __init__(self) -> None:
        self.logger = logging.getLogger("AppManager")
        self.logger.setLevel(logging.INFO)

        self.selected_app: Optional[AppRepr] = None  # The currently selected app, if any
        self.app_running: bool = False  # Whether an app should currently be running
        self.app_lock: _thread.LockType = _thread.allocate_lock()

        self.registered_apps: List[AppRepr] = []
        self.scan_for_apps()

    def scan_for_apps(self) -> None:
        """
        Scan for apps in the system and register new ones.
        """
        self.logger.info("Scanning for apps...")
        app_dirs = [d[0] for d in os.ilistdir('/apps') if d[1] == 0x4000]  # 0x4000 is the directory type
        known_apps = {app.app_path: app for app in self.registered_apps}
        for app_dir in app_dirs:
            if app_dir not in known_apps:
                manifest_path = app_dir + '/manifest.json'
                try:
                    with open(manifest_path, 'r') as f:
                        json_data = f.read()
                        app_repr = AppRepr.from_json(app_dir, json_data)
                        self.registered_apps.append(app_repr)
                        self.logger.info(f"Registered app: {app_repr.display_name} from {app_dir}")
                except OSError as e:
                    self.logger.error(f"Failed to read manifest for app in {app_dir}. Skipping. Error: {e}")
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON in manifest for app in {app_dir}. Skipping. Error: {e}")
                except Exception as e:
                    self.logger.error(f"Unexpected error while registering app in {app_dir}. Skipping. Error: {e}")

        for known_app_dir in known_apps.keys():
            if known_app_dir not in app_dirs:
                # App has been removed
                self.registered_apps.remove(known_apps[known_app_dir])
                self.logger.info(f"Removed app: {known_app_dir}")
    
    async def scan_forever(self, interval: float = 5.0) -> None:
        """
        Continuously scan for apps at a specified interval.
        :param interval: Time in seconds between scans.
        """
        while True:
            self.scan_for_apps()
            await asyncio.sleep(interval)
    
    async def launch_app(self, app_repr: AppRepr) -> None:
        """
        Launch the specified app.
        :param app_repr: The AppRepr instance representing the app to launch.
        """
        if self.app_running:
            # we need to stop the currently running app first
            self.app_running = False
            self.logger.info(f"Stopping currently running app: {self.selected_app.display_name if self.selected_app else 'None'}")
            # The app should see that it's supposed to stop because app_running is set to False.
            # we'll know when that happens because it will release the app_lock.
            try:
                await acquire_lock(self.app_lock, timeout=5.0)
            except TimeoutError as e:
                self.logger.error(f"Failed to stop the currently running app within timeout: {e}")
                # TODO: figure out how to hard-stop the other thread.
                return
            # once we have it, we can release it - the app thread should have stopped itself
            self.app_lock.release()
        
        # Now we can start the new app
        self.selected_app = app_repr
        self.logger.info(f"Creating app thread for: {app_repr.display_name} from {app_repr.app_path}")
        self.app_running = True
        _thread.start_new_thread(app_thread, (app_repr, self))