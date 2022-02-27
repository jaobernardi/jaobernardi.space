from types import GeneratorType
import pyding
import socket, ssl
from threading import Thread


class Client:
    def __init__(self, connection, address):
        # placeholder
        self.connection = connection
        self.address = address
    
    def send_data(self, data):
        return self.connection.send(data, )

    def read_data(self):
        # Init the request
        request = Request()
        # Get the data from the client and only stop if there is no more data or request is done.
        while not request.complete:
            # Recieve data
            new_data = self.connection.recv(1)
            # Break if no data is recieved
            if not new_data:
                break
            # Append new data
            request.append_raw_data(new_data)
        # Process the request
        self.process_data(request)
        self.close_connection()

    def close_connection(self):
        self.connection.close()

    def process_data(self, data):
        event = pyding.call("http_request", request=data)
        if event.response:
            for content in event.response.output():
                self.send_data(content)
        


class Response:
    def __init__(self, status_code, status_message, headers={}, data=b""):
        self.status_code = status_code
        self.status_message = status_message
        self.headers = headers
        self.data = data        
    
    def output(self):
        head = f"HTTP/1.1 {self.status_code} {self.status_message}".encode("utf-8")
        for header in self.headers:
            head += f"\r\n{header}: {self.headers[header]}".encode("utf-8")

        yield head
        if self.data:
            yield b"\r\n\r\n"
            if isinstance(self.data, GeneratorType):
                for i in self.data:
                    yield i
            else:
                yield self.data


class Request:
    def __init__(self, raw_data: bytes = b""):
        self.raw_data = raw_data
        self.parse_raw_data()

    def parse_raw_data(self):
        self.method = None
        self.path = None
        self.query_string = {}
        self.headers = {}
        self.data = None
        self.complete = False

        index = 0
        head, *body = self.raw_data.split(b"\r\n\r\n")
        # TODO: Rewrite this bit
        for line in head.split(b"\r\n"):
            line = line.decode("utf-8")
            if " " in line and index == 0:
                self.method, *other = line.split(" ")
                self.path = other[0] if other else ""
                self.path = self.path.split("?")[0]
                if "?" in other[0] and "=" in other[0]:
                    self.query_string = "?".join(other[0].split("?")[1:])
                                       
                    self.query_string = {k: v for k, v in [i.split("=") for i in self.query_string.split("&")]}

            elif index > 0:
                line = line.removesuffix("\r\n").split(": ")
                if line[0]:
                    self.headers[line[0]] = "".join(line[1:])
            index += 1
        if "Content-Length" in self.headers and body:
            body = [body] if not isinstance(body, list) else body
            body = b"\r\n\r\n".join(body)
            self.data = body  
            if len(body) >= int(self.headers["Content-Length"]):
                self.complete = True

        elif b"\r\n\r\n" in self.raw_data:
            self.complete = True
                

    def append_raw_data(self, raw_data):
        self.raw_data += raw_data
        self.parse_raw_data()

class Server:
    """
        Server
        ------
        A simple http server.
    """
    def __init__(self, host: str, port: int, private_key: str = "", chain: str = "", use_https: bool = False):
        self.host = host
        self.port = port
        self.private_key = private_key
        self.chain = chain
        self.use_https = use_https
        self.running = False

    def spin_up(self):
        if self.use_https:
            # TODO: Implement HTTPS stuff etc etc
            raise NotImplemented("Socket ssl wrapping not implemented.")

        # Setup socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen()

        # Pass to the main loop
        self.running = True
        self.run()

    def run(self):
        while self.running:
            client = Client(*self.socket.accept())
            thread = Thread(target=client.read_data, daemon=True)
            thread.start()