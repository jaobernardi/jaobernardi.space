from lib import web, utils


def main():
    __import__("handlers.home")
    # Setup server
    server = web.Server("0.0.0.0", 1220)
    server.spin_up()


if __name__ == "__main__":
    utils.load_handlers()
    main()

