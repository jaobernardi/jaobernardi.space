from .web import Server
import pyding
import socket, threading

class RelayClient:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
    
    def send_data(self, data):
        self.connection.send(data)

    def read_data(self):
        data = b""
        while True:
            new_data = self.connection.recv(1024)
            if not new_data or data.endswith(b"\n\n"): break
            data += new_data
        self.handle_data(data)

    def handle_data(self, data):
        print(data)
        if data == b"keep-alive":
            print("is-keep-alive")
            self.send_data(b"keep-alive")


class RelayServer(pyding.EventSupport, Server):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.running = False
        self.register_events()
        self.connections = []

    def handle_connection(self, connection, address):
        client = RelayClient(connection, address)
        self.connections.append(client)
        threading.Thread(target=client.read_data).start()
        connection.send(f"Relay@{self.port}#{address}".encode("utf-8"))


    def broadcast(self, message):
        for client in self.connections:
            try:
                client.send_data(message)
            except:
                pass

    @pyding.on("relay_broadcast")
    def event_broadcast(self, event, message):
        self.broadcast(message)


def client_test(h, p):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((h, p))        
        while True:
            data = s.recv(1024)
            print('Received', data)
            s.send(b"keep-alive")
