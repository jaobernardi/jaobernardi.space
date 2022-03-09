from time import sleep
import pyding
import logging


class RelayController(pyding.EventSupport):
    def __init__(self):
        # Init pyding events
        self.register_events()
        self.connections = []
        self.running = False
        self.broadcasting = False

    def spin_up(self):
        self.running = True
        while self.running:
            # Broadcast a keep-alive to prevent connections from timing out
            self.broadcast(b"{}")
            sleep(10)
    
    @pyding.on("relay_add")
    def add_connection(self, event, client, request):
        self.connections.append([client, request])

    def broadcast(self, message):
        if self.broadcasting:
            # Prevent broadcasting data while transmitting data
            while self.broadcasting:
                logging.info(f"Waiting to broadcast {message}")
                continue
    
        self.broadcasting = True
        for client, req in self.connections:
            try:
                client.send_data(message+b"\n")
            except Exception as e:
                logging.info("Failed to send broadcast to "+client.address[0])
        self.broadcasting = False


    @pyding.on("relay_broadcast")
    def event_broadcast(self, event, message):
        self.broadcast(message)
