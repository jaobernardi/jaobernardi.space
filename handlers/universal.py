from wsgiref import headers
import pyding
from lib import web, config, html_parsing
import logging

headers = {"X-Backend": "Universal", "Server": "jdspace"}

@pyding.on("http_request", priority=float("inf"))
def universal_files(event, request: web.Request, client: web.Client):
    if "Host" not in request.headers:
        return web.Response(
            400,
            "Bad Request",
            headers,
            b""
        )
    match request.path.split("/")[-1]:
        case "robots.txt":
            robots = open("www/robots.txt", "rb")
            robots = robots.read()
            return web.Response(
                200,
                "OK",
                {
                    "Content-Type": "text/plain",
                    "Content-Length": len(robots),
                } | headers,
            robots
            )
        case "favicon":
            favicon = open("assets/favicon.png", "rb")
            favicon = favicon.read()
            return web.Response(
                200,
                "OK",
                {
                    "Content-Type": "image/png",
                    "Content-Length": len(favicon),
                } | headers,
            favicon
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
            return web.Response(200, "OK", {"Content-Type": "text/html", "Content-Length": len(data)}|headers, data)
