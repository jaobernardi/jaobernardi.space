import pyding
from lib import web, config
import logging


@pyding.on("http_request")
def auth_handler(event, request: web.Request, client: web.Client):
    if "Host" not in request.headers or request.headers["Host"] != "auth.jaobernardi.space":
        return
    return web.Response(204, "No Content", {"X-Backend": "Auth"})