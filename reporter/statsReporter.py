
import sys
import socket


class StatsReporter:
    def __init__(
        self,
        socket_type,
        socket_address,
        encoding='utf-8',
        formatter=None
    ):
        self._socket_type = socket_type
        self._socket_address = socket_address
        self._encoding = encoding
        self._formatter = formatter
        self.create_socket()

    def create_socket(self):
        try:
            sock = socket.socket(*self._socket_type)
            # no sock.connect
            self._sock = sock
        except socket.error as e:
            pass

    def close_socket(self):
        try:
            self._sock.close()
        except (AttributeError, socket.error) as e:
            pass

    def send_data(self, data):
        try:
            sent = self._sock.sendto(data.encode(self._encoding),self._socket_address)

        except (AttributeError, socket.error) as e:

            # attempt to recreate socket on error
            self.close_socket()
            self.create_socket()

