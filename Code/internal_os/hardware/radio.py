""" Abstraction of the radio driver """
from machine import I2C, Pin, unique_id


try:
    from typing import List
except ImportError:
    # we're on an MCU, typing is not available
    pass

from sx1262 import SX1262
import logging

sx = SX1262(
    spi_bus=0,
    clk=18, mosi=19, miso=20,
    cs=21, irq=17, rst=23, gpio=22
)

class Packet:
    """
    Represents a packet.
    """
    def __init__(self, dest: bytes, app_number: bytes, data: bytes):
        self.source = unique_id().hex()[-4:].encode()
        self.dest = dest
        self.app_number = app_number
        self.data = data

    def __repr__(self):
        return f"Packet(source={self.source}, dest={self.dest}, app_number={self.app_number}, data={self.data})"
    
    def to_dict(self):
        """
        Convert the contact to a dictionary representation.
        """
        return {
            'source': self.source,
            'dest': self.dest,
            'app_number': self.app_number,
            'data': self.data,
        }

class BadgeRadio:
    
    def __init__(self) -> None:
        self._receive_queue = []  # rx queue
        self._transmit_queue = [] # tx queue
        sx.begin(
            freq=923, bw=500.0, sf=12, cr=8, syncWord=0x12,
            power=14, currentLimit=60.0, preambleLength=8, # max power!
            implicit=False, implicitLen=0xFF,
            crcOn=True, txIq=False, rxIq=False,
            tcxoVoltage=0, useRegulatorLDO=False, # crystal, dcdc regulator
            blocking=False # used with a callback
        )
        sx.setBlockingCallback(False, self._lora_callback)

    def _lora_callback(self, events):
        if events & SX1262.RX_DONE:
            msg, status = sx.recv()
            self._handle_packet(msg)

    def send_msg(self, dest: bytes, target_app: bytes, message: bytes):
        """
        Sends a message over LoRa.
        Takes in app ID, and optional message type. If ommited, it's an announcement.
        """
        
        """ bytes 0-1: source addr
        bytes 2-3: dest addr
        bytes 4-5: packet type
        bytes 6-254: app-specific payload """
        
        src = unique_id().hex()[-4:]
        src_bytes = bytes.fromhex(src)

        msg_bytes = bytearray(6 + len(message))
        msg_bytes[0:2] = src_bytes
        msg_bytes[2:4] = dest
        msg_bytes[4:6] = target_app
        msg_bytes[6:] = message

        sx.send(msg_bytes)

    def _handle_packet(self, packet) -> None:
        """ 
        Directs to target app API
        TODO: implement app dispatching in internal_os
        """
        if not packet or len(packet) < 6:
            logging.warning("Received malformed packet")
            return

        src = packet[0:2]
        dest = packet[2:4]
        target_app = packet[4:6]
        payload = packet[6:]

        pkt = Packet(dest, target_app, payload)
        self._receive_queue.append(pkt)  # add packet to the rx queue

        # TODO: dispatch a radio packet
        #internal_os.dispatch_packet(src, dest, target_app, payload)

    def get_packets_available(self) -> int:
        """
        Returns the number of packets available in the receive queue.
        """
        return len(self._receive_queue)

    def get_next_packet(self):
        """
        Retrieves and removes the next packet from the receive queue.
        Returns None if the queue is empty.
        """
        if self._receive_queue:
            return self._receive_queue.pop(0)
        return None
    
    def get_send_queue_size(self) -> int:
        """
        Returns the number of packets in the send queue.
        """
        return len(self._transmit_queue)

    def get_time_to_next_send(self) -> int:
        """
        Returns the time in seconds until the next packet can be sent.
        """

        # TODO: placeholder
        if not self._transmit_queue:
            return 0
        # assuming a rate limit of 1 packet per second
        return 1