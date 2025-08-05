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

def send_packet(packet: Packet) -> None:
    """
    Sends a packet over the radio.
    Send a packet. To avoid flooding the radio bandwidth, this method can only send packets at a rate of 1 per second. Any additional packets are added to a queue.

    """

    if not isinstance(packet, Packet):
        raise TypeError("packet must be an instance of Packet.")
    selected_app = internal_os.apps.selected_app
    if selected_app is None:
        raise AttributeError("no app is currently selected; cannot retrieve app_number.")
    app_number = selected_app.app_number
    internal_os.radio.send_msg(packet.dest, int(app_number).to_bytes(2), packet.data)

def get_send_queue_size() -> int:
    """
    Returns the number of packets in the send queue.
    """
    return internal_os.radio.get_send_queue_size()

def get_time_to_next_send() -> int:
    """
    Returns the time in seconds until the next packet can be sent.
    """
    return internal_os.radio.get_time_to_next_send()