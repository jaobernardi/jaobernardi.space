from urllib.parse import quote
import pyding
from lib import web, config
import logging


@pyding.on("http_request", host="auth.jaobernardi.space")
def auth_handler(event, request: web.Request, client: web.Client, host: str):
    match request.method, request.path.split("/")[1:], request.query_string:
        case "GET", ["spotify", "authenticate"], _params:            
            return web.Response.redirect(
                f"https://accounts.spotify.com/authorize?response_type=code&client_id={config.get_spotify_client_id()}&scope=user-modify-playback-state user-read-currently-playing user-read-playback-state streaming&redirect_uri=https://auth.jaobernardi.space/spotify/callback",
                {"X-Backend": "Auth"}
            )

        case "GET", ["spotify", "callback"], {"code": code, "state": state, **_params}:
            asset = open(f"assets/spotify/access_success.html", "rb")
            asset = asset.read()
            content_type = "text/html"

            return web.Response.ok(asset, content_type, {"X-Backend": "Auth"})

        case "GET", ["spotify", "callback"], _params:
            asset = open(f"assets/spotify/access_fail.html", "rb")
            asset = asset.read()
            content_type = "text/html"

            return web.Response.ok(asset, content_type, {"X-Backend": "Auth"})

        case _:
            return web.Response(204, "No Content", {"X-Backend": "Auth"})