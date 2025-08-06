from internal_os.internalos import BadgeRadio
from internal_os.internalos import InternalOS
from internal_os.hardware.radio import Packet

internal_os = InternalOS.instance()

def get_packets_available() -> int:
    """
    Returns the number of packets available in the radio's receive buffer.
    """
    return internal_os.radio.get_packets_available()

def read_packet() -> Packet | None:
    """
    Reads the next available packet from the badges's receive queue.
    returns the next Packet object if available, otherwise None.
    """
    return internal_os.radio.get_next_packet()

def send_packet(dest: int, data: bytes) -> None:
    """
    Sends a packet over the radio.
    Send a packet. To avoid flooding the radio bandwidth, this method can only send packets at a rate of 1 every 1.5 seconds. Any additional packets are added to a queue.

    """

    selected_app = internal_os.apps.get_current_app_repr()
    if selected_app is None:
        raise AttributeError("no app is currently selected; cannot retrieve app_number.")
    app_number = selected_app.app_number
    if any([p.app_number == app_number for p in internal_os.radio._transmit_queue]):
        raise RuntimeError(f"App {selected_app.display_name} already has a packet in the transmit queue. Please wait until it is sent before sending another packet. (See get_send_queue_size())")
    internal_os.radio.add_to_tx_queue(dest, app_number, data)

def get_send_queue_size() -> int:
    """
    Returns the number of packets in the send queue.
    """
    return internal_os.radio.get_send_queue_size()

def get_time_to_next_send() -> float:
    """
    Returns the time in seconds until the next packet can be sent.
    """
    return internal_os.radio.get_time_to_next_send()