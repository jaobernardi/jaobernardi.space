import ssl
import socket

class Server:
    """
        Server
        ------
        A simple server.
    """
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.running = False

    def stop(self):
        self.socket.close()
        self.running = False

    def setup_socket(self):
        # Setup socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start_socket(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen()

    def spin_up(self):
        self.setup_socket()
        self.start_socket()
        self.running = True
        # Pass to the main loop
        self.run()

    def handle_connection(self, connection, address):
        connection.close()

    def run(self):
        while self.running:
            try:
                self.handle_connection(*self.socket.accept())
            except KeyboardInterrupt:
                self.running = False
                break
            except:
                pass
        self.socket.close()

class SSLServer(Server):
    """
    SSLServer
    ----------
    A Simple SSL socket server.
    """
    def __init__(self, host: str, port: int, private_key: str = "", chain: str = ""):
        super().__init__(host, port)
        self.private_key = private_key
        self.chain = chain
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(chain, private_key)

    def start_socket(self):
        super().start_socket()
        self.socket = self.context.wrap_socket(self.socket, server_side=True)
