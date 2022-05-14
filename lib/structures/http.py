from .client import Client
from .response import Response
from .server import Server

from threading import Thread
import ssl


class HTTPServer(Server):
    """
    HTTPServer
    ----------
    A Simple http server.
    """
    def __init__(self, host: str, port: int, private_key: str = "", chain: str = "", use_https: bool = False):
        super().__init__(host, port)
        self.private_key = private_key
        self.chain = chain
        self.use_https = use_https
        if chain and private_key and use_https:
            self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.context.load_cert_chain(chain, private_key)

    def start_socket(self):
        super().start_socket()
        if self.use_https:
            self.socket = self.context.wrap_socket(self.socket, server_side=True)

    def handle_connection(self, connection, address):
        # Create the client object and call events
        client = Client(connection, address, self)
        if True:
            thread = Thread(target=client.read_data, daemon=True)
            thread.start()
        else:
            client.close_connection()


class HTTPRedirecterServer(HTTPServer):
    def __init__(self, host: str, port: int, location: str, private_key: str = "", chain: str = "", use_https: bool = False):
        super().__init__(host, port, private_key, chain, use_https)
        self.location = location

    def handle_connection(self, connection, address):
        response = Response(301, "Permanent Redirect", {"X-Backend": "HTTPS-Redirects", "Location": self.location}, b" ")
        for content in response.output():
            connection.send(content)