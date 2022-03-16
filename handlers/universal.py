import pyding
from lib import web, config, html_parsing
import logging


@pyding.on("http_request", priority=float("inf"))
def universal_files(event, request: web.Request, client: web.Client):
    if "Host" not in request.headers:
        return web.Response(
            400,
            "Bad Request",
            {"Server": "jdspace"},
            b""
        )

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

    # Don't bother the APIS, they're too busy on their own.
    if request.headers["Host"] in ["api.jaobernardi.space", "services.jaobernardi.space"]:
        # Match a service name
        service_name = {"api.jaobernardi.space": "API", "services.jaobernardi.space": "Serviços Gerais"}[request.headers['Host']]

        if "User-Agent" in request.headers and "Twitterbot" in request.headers["User-Agent"]:
            # Serve data to twitter bot
            logging.info("Serving data for Twitterbot")
            data = ("<!DOCTYPE html>"
            '<html lang="en">'
            '<head>'
                '<meta name="twitter:card" content="summary" />'
                '<meta name="twitter:site" content="@jaobernard" />'
                f'<meta name="twitter:title" content="{service_name} | JDSpace" />'
                '<meta name="twitter:image" content="https://jaobernardi.space/jdspace.png" />'
            "</head>"
            "<body>" 
            "</body>"
            "</html>").encode("utf-8")
            return web.Response(200, "OK", {"Server": "jdspace", "Content-Type": "text/html", "Content-Length": len(data)}, data)
