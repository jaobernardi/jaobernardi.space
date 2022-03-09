from time import sleep, time
import pyding
import logging


class RelayController(pyding.EventSupport):
    def __init__(self):
        # Init pyding events
        self.register_events()
        self.connections = []
        self.running = False
        self.last_broadcast = 0

    def spin_up(self):
        while self.running:
            if (time()-self.last_broadcast) > 10:
                self.broadcast(b"{}")
        return

    @pyding.on("relay_add")
    def add_connection(self, event, client, request):
        if [client, request] not in self.connections:
            self.connections.append([client, request])

    def broadcast(self, message):
        self.last_broadcast = time()

        for client, req in self.connections:
            try:
                client.send_data(message+b"\n")
            except Exception as e:
                self.connections.remove([client, req])
                logging.info("Failed to send broadcast to "+client.address[0])



    @pyding.on("relay_broadcast")
    def event_broadcast(self, event, message):
        self.broadcast(message)
