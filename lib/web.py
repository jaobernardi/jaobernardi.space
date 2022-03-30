from cgitb import handler
from types import FunctionType, GeneratorType
from urllib import response
import pyding
import socket, ssl
from threading import Thread


class Client:
    """
    Client
    ------
    A simple wrapper for socket clients for http processing.
    """
    def __init__(self, connection, address, server):
        self.server = server
        self.connection = connection
        self.address = address
    
    def send_data(self, data):
        self.connection.send(data)
        pyding.call("http_downstream", client=self, data=data)     

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

    def close_connection(self):
        self.connection.close()


    def process_data(self, data):
        if not data:
            self.close_connection()
            return

        event = pyding.call("http_request", request=data, client=self, first_response=True)
        if event.response:
            pyding.call("http_response", response=event.response, request=data)
            for content in event.response.output():
                # Transfer control over to a handler.
                if isinstance(content, FunctionType):
                    content(client=self, request=data)
                    pyding.call("http_handover", client=self, handler=content)
                    return
                elif isinstance(content, GeneratorType):
                    for data in content:
                        self.send_data(data)
                    break
                # Send data
                self.send_data(content)
        # Since we're done, close the connection.
        self.close_connection()




class Response:
    """
    Response
    --------
    A simple http response parsing.
    """
    def __init__(self, status_code, status_message, headers={}, data=b" "):
        self.status_code = status_code
        self.status_message = status_message
        self.headers = headers | {"Server": "jdspace", "Connection": "close"}
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
    """
    Response
    --------
    A simple http response forgery.
    """
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
                                       
                    self.query_string = {k: v for k, v in [i.split("=") for i in self.query_string.split("&") if "=" in i]}

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
        if chain and private_key:
            self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.context.load_cert_chain(chain, private_key)

    def start_socket(self):
        super().start_socket()
        if self.use_https:
            self.socket = self.context.wrap_socket(self.socket, server_side=True)

    def handle_connection(self, connection, address):
        # Create the client object and call events
        client = Client(connection, address, self)
        if not pyding.call("http_client", cancellable=True, blocking=False, client=client).cancelled:
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