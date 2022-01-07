from space import web
import logging
import pyding

logging.basicConfig(level=logging.INFO)
print(":)")


@pyding.on("http_request", priority=1000)
def api(event, request, connection, address):
    if "Host" in request.headers and request.headers["Host"] == "api.jaobernardi.space":
        event.cancel()
        return web.response(201, 'No content', {'Server': 'jaobernardi/backend'}, b"")