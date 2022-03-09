from .web import Server
import pyding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

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
    def __init__(self, host: str, port: int, private_key: str):
        self.host = host
        self.port = port
        self.running = False
        self.register_events()
        self.connections = []
        with open(private_key, "rb") as key_file:
            self.private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
        self.public_key = self.private_key.public_key()
    def handle_connection(self, connection, address):
        client = RelayClient(connection, address)
        self.connections.append(client)
        threading.Thread(target=client.read_data).start()
        connection.send(f"Relay@{self.port}#{address}".encode("utf-8"))


    def broadcast(self, message):
        message = self.public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        for client in [i for i in self.connections]:
            try:
                client.send_data(message)
            except:
                self.connections.remove(client)

    @pyding.on("relay_broadcast")
    def event_broadcast(self, event, message):
        self.broadcast(message)
