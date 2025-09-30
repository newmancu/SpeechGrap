import socket
import json

from .config import DynSettings
from .logs import logger


class DisplayUnixClient:
    def __init__(self, ds: DynSettings):
        self.ds = ds
        self.socket_path = ds.display_socket.value
        self.socket = None

    def connect(self):
        if not self.ds.display_notifier_is_on.value:
            logger.debug("Display notification is off")
            return
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(self.socket_path)
            return True
        except Exception as e:
            logger.error(f"Cannot connect: {e}")
            return False

    def send_command(self, title: str, message: str):
        if not self.socket:
            logger.warning("No socket")
            return
        if not self.ds.display_notifier_is_on.value:
            logger.debug("Display notification is off")
            return
        try:
            msg = dict(cmd="NOTIFY", title=title, message=message)
            json_data = json.dumps(msg).encode("utf-8")
            self.socket.send(json_data + b"\n")
            response = self.socket.recv(1024).decode("utf-8")
            return response

        except Exception as e:
            logger.error(f"Cannot send command: {e}")
            return

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    def __del__(self):
        self.close()
