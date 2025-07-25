import logging

class BaseApp:
    """
    An abstract class that applications must inherit from.
    """
    logger: logging.Logger # set up by the app launcher
    def on_open(self) -> None:
        """
        Run once when the app is launched.
        This method should be overridden by the app.
        """
        raise NotImplementedError("on_open must be implemented by the app.")
    
    def loop(self) -> None:
        """
        The main loop of the app.
        Called repeatedly while the app is running.
        """
        raise NotImplementedError("loop must be implemented by the app.")
    
    def on_wake_from_lpm(self) -> None:
        """
        Called when the app is woken from low power mode.
        This method should be overridden by the app if needed.
        """
        pass

    def before_close(self) -> None:
        """
        Called before the app is closed. Should e.g. save state to the FS if needed.
        Has an enforced 200ms limit.
        This method should be overridden by the app if needed.
        """
        pass

    def on_packet_while_not_active(self, packet) -> None:
        """
        Called if the app is configured to be woken if it receives a packet while not active.
        Most APIs (e.g. `display`, `input`, etc.) will not be available in this method.
        Intended to e.g. send a message or modify a file.
        """
        pass