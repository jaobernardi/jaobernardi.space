from lib import web, utils, relay, config
import threading

def main():
    # Setup server
    relay_server = relay.RelayServer(**config.get_relay())
    thread = threading.Thread(target=relay_server.spin_up, daemon=True)
    thread.start()

    server = web.HTTPServer(**config.get_web())
    thread = threading.Thread(target=server.spin_up, daemon=True)
    thread.start()

    while True:
        pass

if __name__ == "__main__":
    utils.load_handlers()
    main()

