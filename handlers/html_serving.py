import pyding
from lib import web, config
from os import path


@pyding.on("http_request", priority=float("inf"))
def html_route(event, request: web.Request, client: web.Client):
    if "Host" not in request.headers or request.headers["Host"] != "jaobernardi.space":
        return

    if request.path == "/jdspace.png":
        jdspace_logo = open("assets/jdspace.png", "rb")
        jdspace_logo = jdspace_logo.read()
        return web.Response(
            200,
            "OK",
            {"Server": "jdspace",
            "Content-Type": "image/png",
            "Content-Length": len(jdspace_logo)},
        jdspace_logo
        )