from space import web
import logging
import pyding

logging.basicConfig(level=logging.INFO)
print(":)")
@pyding.on("http_request")
def api(event, request, connection, address):
    print(":)", request.headers)
    if "Host" in request.headers and request.headers["Host"] == "api.jaobernardi.space":
        return web.response(201, 'No content', {'Server': 'jaobernardi/backend'}, b"")