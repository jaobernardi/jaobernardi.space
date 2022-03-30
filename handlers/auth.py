import pyding
from lib import web, config
import logging


@pyding.on("http_request")
def auth_handler(event, request: web.Request, client: web.Client):
    return web.Response(204, "No Content", {"X-Backend": "Auth"})