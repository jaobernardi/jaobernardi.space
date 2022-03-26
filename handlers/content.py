from wsgiref import headers
import pyding
from lib import web, config, html_parsing
import logging

headers = {"X-Backend": "Universal", "Server": "jdspace"}
service_name = {
    "api.jaobernardi.space": "API",
    "services.jaobernardi.space": "Serviços Gerais",
    "jaobernardi.space": "Home"
}


@pyding.on("http_request", priority=float("inf"))
def cdn_serving(event, request: web.Request, client: web.Client):
    if "Host" not in request.headers or request.headers["Host"] != "content.jaobernardi.space":
        return

    # Serving universal files
    filename = request.path.split("/")[-1]
    match filename:
        case "jdspace.png" | "archive.png":
            asset = open(f"assets/{filename}", "rb")
            asset = asset.read()
            return web.Response(
                200,
                "OK",
                {
                    "Content-Type": "image/png",
                    "Content-Length": len(asset),
                } | headers,
                asset
            )