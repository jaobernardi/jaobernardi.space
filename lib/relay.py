from .web import Server
import pyding
import threading


class RelayClient:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
    
    def send_data(self, data):
        self.connection.send(data)

    def read_data(self):
        while True:
            data = self.connection.recv(1024)
            if not data or data.endswith(b"\n\n"): break
            self.handle_data(data)
        self.connection.close()

    def handle_data(self, data):
        return



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


    def broadcast(self, message):
        for client in [i for i in self.connections]:
            try:
                client.send_data(message)
            except:
                self.connections.remove(client)

    @pyding.on("relay_broadcast")
    def event_broadcast(self, event, message):
        self.broadcast(message)
