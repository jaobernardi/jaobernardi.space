from lib import web, utils, relay, config
import threading
import logging

logging.basicConfig(level=logging.INFO)

def main():
    # Setup server
    relay_server = relay.RelayController()
    thread = threading.Thread(target=relay_server.spin_up, daemon=True)
    thread.start()

    if config.get_https_redirect():
        http_redirect = web.HTTPRedirecterServer(**config.get_https_redirect_settings())
        thread = threading.Thread(target=http_redirect.spin_up, daemon=True)
        thread.start()
    server = web.HTTPServer(**config.get_web())
    server.spin_up()


if __name__ == "__main__":
    utils.load_handlers()
    main()

