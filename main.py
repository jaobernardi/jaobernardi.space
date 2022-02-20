from lib import web


def main():
    __import__("handlers.home")
    # Setup server
    server = web.Server("127.0.0.1", 1220)
    server.spin_up()


if __name__ == "__main__":
    main()

