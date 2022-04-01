from wsgiref import headers
import pyding
from lib import web, config, html_parsing
import logging

headers = {"X-Backend": "Universal"}
service_name = {
    "api.jaobernardi.space": "API",
    "services.jaobernardi.space": "Serviços Gerais",
    "jaobernardi.space": "Home"
}


@pyding.on("http_request", priority=99)
def universal_files(event, request: web.Request, client: web.Client, host: str):
    # Serving universal files
    filename = request.path.split("/")[-1]
    host = request.headers['Host'] if 'Host' in request.headers else None
    match filename, host:
        case "robots.txt", host:
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

        case "favicon" | "favicon.ico", host:
            favicon = open("assets/images/favicon.ico", "rb")
            favicon = favicon.read()
            return web.Response(
                200,
                "OK",
                {
                    "Content-Type": "image/x-icon",
                    "Content-Length": len(favicon),
                } | headers,
                favicon
            )
        
        case "jdspace.png" | "archive.png", host if host != "content.jaobernardi.space":

            return web.Response(
                301,
                "Moved Permanently",
                {
                    "Location": f"https://content.jaobernardi.space/{filename}",
                } | headers,
                b" "
            )

    # Prevent invalid requests
    if "Host" not in request.headers:
        return web.Response(
            400,
            "Bad Request",
            headers,
            b""
        )
    
    
    # Don't bother the APIS, they're too busy on their own.
    if request.headers["Host"] in service_name:
        # Match a service name
        service = service_name[request.headers['Host']]
        
        # Serve cards to Twitter
        if "User-Agent" in request.headers and "Twitterbot" in request.headers["User-Agent"]:
            # Serve data to twitter bot
            logging.info("Serving data for Twitterbot")
            data = ("<!DOCTYPE html>"
                    '<html lang="en">'
                    '<head>'
                        '<meta name="twitter:card" content="summary" />'
                        '<meta name="twitter:site" content="@jaobernard" />'
                        f'<meta name="twitter:title" content="{service} | JDSpace" />'
                        '<meta name="twitter:image" content="https://content.jaobernardi.space/jdspace.png" />'
                    "</head>"
                    "<body>" 
                    "</body>"
                    "</html>")\
                .encode("utf-8")
            return web.Response(
                200,
                "OK",
                {
                    "Content-Type": "text/html",
                    "Content-Length": len(data)
                }|headers,
                data
            )
