import pyding
import socket, ssl
from . import exceptions

class Client:
    def __init__(self, client, address):
        # placeholder
        self.client = client
        self.address = address
    
    def send_data(self, data):
        return #TODO: implement this thing here


class Server:
    """
        Server
        ------
        A simple http server.
    """
    def __init__(self, host: str, port: int, private_key: str, chain: str, use_https: bool = False, threaded: bool = True):
        self.host = host
        self.port = port
        self.private_key = private_key
        self.chain = chain
        self.use_https = use_https
        self.threaded = threaded

    def spin_up(self):
        if self.use_https:
            # TODO: Implement HTTPS stuff etc etc
            raise NotImplemented("Socket ssl wrapping not implemented.")

        # Setup socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT)

        # Pass to the main loop
        self.run()
    