from lib import web, utils, relay, config
import threading
import logging

logging.basicConfig()

def main():
    # Setup server
    relay_server = relay.RelayServer()
    thread = threading.Thread(target=relay_server.spin_up, daemon=True)
    thread.start()

    server = web.HTTPServer(**config.get_web())
    target=server.spin_up()
    while True:
        pass

if __name__ == "__main__":
    utils.load_handlers()
    main()

