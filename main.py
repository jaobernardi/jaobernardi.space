from lib import web, utils


def main():
    # Setup server
    server = web.Server("0.0.0.0", 1025)
    server.spin_up()


if __name__ == "__main__":
    utils.load_handlers()
    main()

