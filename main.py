from lib import web, utils, relay
import threading

def main():
    # Setup server
    relay_server = relay.RelayServer("0.0.0.0", 1026)
    thread = threading.Thread(target=relay_server.spin_up, daemon=True)
    thread.start()

    server = web.HTTPServer("0.0.0.0", 1025)
    server.spin_up()


if __name__ == "__main__":
    utils.load_handlers()
    main()

