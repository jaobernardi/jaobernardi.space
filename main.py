from lib import web
import pyding


# Handle http requests
@pyding.on("http_request")
def responder(event, request):
    # Always return 200 OK
    return web.Response(200, "OK", data=request.data)


def main():
    # Setup server
    server = web.Server("127.0.0.1", 1220)
    server.spin_up()


if __name__ == "__main__":
    main()

