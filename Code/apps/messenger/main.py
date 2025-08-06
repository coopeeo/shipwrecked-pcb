import badge
from micropython import mem_info
from machine import unique_id
import struct
import logging
import gc
print(f"Free memory before import: {gc.mem_free()} bytes")
gc.collect()  # Collect garbage to free up memory
print(f"Free memory after collect: {gc.mem_free()} bytes")
from ellipticcurve import PublicKey, Ecdsa, Signature
print(f"Free memory after imports: {gc.mem_free()} bytes")
gc.collect()  # Collect garbage again after imports
print(f"Free memory after second collect: {gc.mem_free()} bytes")

with open(badge.util.get_data_dir() + "/announcement_key.txt", "r") as f:
    announcement_key_raw = f.read()
    vk = PublicKey.fromCompressed(announcement_key_raw)

# ANNOUNCEMENT FORMAT:
# 1 byte: reserved (should be 0)
# 32 bytes: r-value of the ECDSA signature of the rest of the message
# 32 bytes: s-value of the ECDSA signature
# 4 bytes: announcement creation time (Unix timestamp, also serves as announcement ID)
# 1 byte: length of the message, in bytes
# 179 bytes: message text, padded with null bytes
MSG_FMT = "!B32s32sIB179s"
SIGLESS_MSG_FMT = "!IB179s"

class Message:
    creation_timestamp: int
    message: str
    signature: Signature
    signature_valid: bool

    def __init__(self, creation_timestamp: int, message: str, signature: Signature) -> None:
        self.creation_timestamp = creation_timestamp
        self.message = message
        self.signature = signature
        self._signature_valid = None
    
    def is_signature_valid(self) -> bool:
        if self._signature_valid is not None:
            return self._signature_valid
        sigless_msg = struct.pack(SIGLESS_MSG_FMT, self.creation_timestamp, len(self.message), self.message.encode('utf-8') + b'\x00' * (195 - len(self.message)))
        self._signature_valid = Ecdsa.verify(sigless_msg, self.signature, vk)
        return self._signature_valid

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Message':
        logger = logging.getLogger("Message.from_bytes")

        if len(data) != struct.calcsize(MSG_FMT):
            raise ValueError("Invalid message data length")
        reserved, sigr, sigs, creation_timestamp, length, message = struct.unpack(MSG_FMT, data)
        if reserved != 0:
            logger.warning("Reserved byte is not zero, this badge is probably outdated")
        signature = Signature(int.from_bytes(sigr, 'big'), int.from_bytes(sigs, 'big'))

        return cls(creation_timestamp, message.decode().rstrip('\x00'), signature)        

    def to_bytes(self) -> bytes:
        """Convert the message to raw bytes"""
        reserved = 0
        length = len(self.message)
        if length > 195:
            raise ValueError("Message is too long")
        message_padded = self.message + '\x00' * (195 - length)  # Pad with null bytes
        message_bytes = message_padded.encode('utf-8')
        return struct.pack(MSG_FMT, reserved, self.signature, self.creation_timestamp, length, message_bytes)
    
    def __repr__(self) -> str:
        return f"Message(creation_timestamp={self.creation_timestamp}, message='{self.message}', signature_valid={self.signature_valid}, signature={self.signature} (r={self.signature.r}, s={self.signature.s}))"

class App(badge.BaseApp):
    def __init__(self) -> None:
        self.last_button = False
        self.received_message = None

    def get_last_displayed_message_timestamp(self) -> int:
        try:
            with open(badge.util.get_data_dir() + "/last_displayed_timestamp.txt", "r") as f:
                timestamp = int(f.read())
                return timestamp
        except Exception as e:
            self.logger.error(f"Failed to load last displayed timestamp: {e}")
            return 0
    
    def set_last_displayed_message_timestamp(self, timestamp: int) -> None:
        try:
            with open(badge.util.get_data_dir() + "/last_displayed_timestamp.txt", "w") as f:
                f.write(str(timestamp))
        except Exception as e:
            self.logger.error(f"Failed to save last displayed timestamp: {e}")

    def on_open(self) -> None:
        try:
            with open(badge.util.get_data_dir() + "/last_packet.bin", "rb") as f:
                data = f.read()
                if data:
                    message = Message.from_bytes(data)
                    self.logger.info(f"Loaded last packet from file: {message}")
                    if self.should_display_message(message):
                        self.received_message = message
        except Exception as e:
            self.logger.error(f"Failed to load last packet from file: {e}")

    def loop(self) -> None:
        if badge.input.get_button(1):
            # TEST: decoding a message
            if not self.last_button:
                message_raw = b'\x00\xe0Eh\xe0f\x9a\xa0\x97=\x01\xefyg\xc5x\xcaF\x9cX\xa8\x1e\xd4\xf1\xf7\xe4%\xb8\xed\xc4\xcaxI\xa1\xdf7~\x0e\xb6\x8f?\xce\x8f\x90\x9d`\xe2\xf4\xa8\xf6\x95>,\x9aGn\x0b:\xba\xc3\x06[%\xa4\xc5h\x93\xbc\xe3%Hello this is another test message :)\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                message = Message.from_bytes(message_raw)
                self.logger.info(f"Message created: {message}")
            self.last_button = True
        else:
            self.last_button = False
        
        if self.received_message:
            self.logger.info(f"Displaying message: {self.received_message}")
            badge.display.fill(1)
            badge.display.nice_text("Announcement", 0, 0, 42)
            badge.display.nice_text(self.received_message.message, 0, 40, 32)
            badge.display.show()
            self.set_last_displayed_message_timestamp(self.received_message.creation_timestamp)
            self.received_message = None

    def save_message(self, messageBytes: bytes) -> None:
        with open(badge.util.get_data_dir() + "/last_message.bin", "wb") as f:
            f.write(messageBytes)

    def should_display_message(self, message: Message) -> bool:
        """
        Confirm that the message is newer than the last one we displayed,
        and that its signature is valid.
        """
        return message.creation_timestamp > self.get_last_displayed_message_timestamp() and message.is_signature_valid()

    def on_packet(self, packet: badge.radio.Packet, is_foreground: bool) -> None:
        # NOTE to people looking at this for inspiration:
        # It is very bad behavoir for most apps to forcibly
        # launch themselves from the background like this.
        # The announcements app is an exception because receiving
        # announcements is quite literally the primary function
        # of the Shipwrecked badge.
        # Again, your apps RFC2119-SHOULD-NOT do this.
        self.logger.info(f"Received message packet: {packet}")
        # verify it so we don't launch/update on a spoofed or old message
        message = Message.from_bytes(packet.data)
        if not self.should_display_message(message):
            self.logger.info(f"Not displaying message: {message}")
            return
        # save the message
        self.save_message(packet.data)

        if not is_foreground:
            # launch the foreground app to display it
            from internal_os.internalos import InternalOS
            import asyncio
            internal_os = InternalOS.instance()
            asyncio.create_task(internal_os.apps.launch_app(internal_os.apps.get_current_app_repr()))
        else:
            self.logger.info(f"Received packet in foreground app")
            self.received_message = message