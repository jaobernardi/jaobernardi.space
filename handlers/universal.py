import pyding
from lib import web, config, html_parsing


@pyding.on("http_request", priority=float("inf"))
def universal_files(event, request: web.Request):
    if request.path == "/robots.txt":
        robots = open("www/robots.txt", "rb")
        robots = robots.read()
        return web.Response(
            200,
            "OK",
            {"Server": "jdspace",
            "Content-Type": "text/plain",
            "Content-Length": len(robots)},
        robots
        )