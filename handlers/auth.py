from urllib.parse import quote
import pyding
from lib import web, config
import logging


@pyding.on("http_request")
def auth_handler(event, request: web.Request, client: web.Client):
    if "Host" not in request.headers or request.headers["Host"] != "auth.jaobernardi.space":
        return

    match request.path.split(" "):
        case ["spotify", "authenticate"]:            
            return web.Response(
                "301",
                "Moved Permanently",
                {
                    "X-Backend": "Auth",
                    "Location": quote(f"https://accounts.spotify.com/authorize?response_type=code&client_id={config.get_spotify_client_id()}&scope=user-modify-playback-state user-read-currently-playing user-read-playback-state streaming&redirect_uri=https://auth.jaobernardi.space/spotify/callback", safe="")
                }
            )
        case ["spotify", "callback"]:
            logging.info(request.query_string)
            return web.Response(204, "No Content", {"X-Backend": "Auth"})
        case _:
            return web.Response(204, "No Content", {"X-Backend": "Auth"})