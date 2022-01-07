from space import web
import logging
import pyding
import json


logging.basicConfig(level=logging.INFO)
print(":)")


@pyding.on("http_request")
def api(event, request, connection, address):
    if "Host" in request.headers and request.headers["Host"] == "api.jaobernardi.space":
        output = {"status": 200, "message": "OK"}


        parsed_output = json.dumps(output)
        return web.response(200, 'No content', {'Server': 'jaobernardi/backend'}, parsed_output.encode("utf-8"))