from time import sleep, time
import pyding
import logging


class RelayController(pyding.EventSupport):
    def __init__(self):
        # Init pyding events
        self.register_events()
        self.connections = {}
        self.running = False

    def spin_up(self):
        self.running = True
        while self.running:
            self.broadcast(b'{"is_keep_alive": true}')
            sleep(30)
        return

    @pyding.on("relay_add", register_ra=False)
    def add_connection(self, event, client, request):
        self.connections[client.address[0]] = client

    def broadcast(self, message):
        # Prevent messing with onging broadcasts

        for client, address in self.connections.items():
            client = self.connections[address]
            try:
                client.send_data(message+b"\r\n")
            except Exception as e:
                self.connections.pop(address)
                logging.info("Failed to send broadcast to "+client.address[0])


    @pyding.on("relay_broadcast", register_ra=False)
    def event_broadcast(self, event, message):
        self.broadcast(message)
