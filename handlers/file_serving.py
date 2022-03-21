import pyding
from lib import web, config
from os import path

headers = {"X-Backend": "Content", "Server": "jdspace"}

@pyding.on("http_request", priority=float("inf"))
def html_route(event, request: web.Request, client: web.Client):
    if "Host" not in request.headers or request.headers["Host"] != "jaobernardi.space":
        return

    if request.path.endswith("jdspace.png"):
        jdspace_logo = open("assets/jdspace.png", "rb")
        jdspace_logo = jdspace_logo.read()
        return web.Response(
            200,
            "OK",
            {
            "Content-Type": "image/png",
            "Content-Length": len(jdspace_logo)
            } | headers,
        jdspace_logo
        )

    elif request.path.endswith("archive.png"):
        archive_logo = open("assets/archive.png", "rb")
        archive_logo = archive_logo.read()
        return web.Response(
            200,
            "OK",
            {
                "Content-Type": "image/png",
                "Content-Length": len(archive_logo)
            } | headers,
        archive_logo
        )
    
    