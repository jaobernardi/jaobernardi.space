from time import sleep
import pyding
import threading


class RelayServer(pyding.EventSupport):
    def __init__(self):
        self.register_events()
        self.connections = []

    def spin_up(self):
        while True:            
            for client, req in self.connections:
                client.send_data(b"keep-alive")
            sleep(10)
    @pyding.on("relay_add")
    def add_connection(self, event, client, request):
        self.connections.append([client, request])

    def broadcast(self, message):
        for client, req in self.connections:
            client.send_data(message+b"\n")


    @pyding.on("relay_broadcast")
    def event_broadcast(self, event, message):
        self.broadcast(message)
