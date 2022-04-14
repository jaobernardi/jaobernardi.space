from wsgiref import headers
import pyding
from lib import web, config, html_parsing
import logging



@pyding.on("http_request", priority=98, host=config.get_hosts()['content']['url'])
def cdn_serving(event, request: web.Request, client: web.Client, host: str):
    # Serving universal files
    filename = request.path.split("/")[-1]
    match filename:
        case "jdspace.png" | "archive.png":
            asset = open(f"assets/images/{filename}", "rb")
            asset = asset.read()
            content_type = "image/png"
        case "style.css":
            asset = open(f"assets/files/{filename}", "rb")
            asset = asset.read()
            content_type = "text/css"

        case _:
            return web.Response(
                404,
                "Not Found",
                {
                    "X-Backend": "CDN"
                }
            )

    return web.Response.ok(
                asset,
                content_type,
                {"X-Backend": "CDN"},
            )