from urllib.parse import quote
import pyding
from lib import web, config
import logging


@pyding.on("http_request", host="auth.jaobernardi.space")
def auth_handler(event, request: web.Request, client: web.Client, host: str):
    match request.path.split("/")[1:]:
        case ["spotify", "authenticate"]:            
            return web.Response(
                "301",
                "Moved Permanently",
                {
                    "X-Backend": "Auth",
                    "Location": f"https://accounts.spotify.com/authorize?response_type=code&client_id={config.get_spotify_client_id()}&scope=user-modify-playback-state user-read-currently-playing user-read-playback-state streaming&redirect_uri=https://auth.jaobernardi.space/spotify/callback"
                    
                }
            )
        case ["spotify", "callback"]:
            logging.info(request.query_string)
            return web.Response(204, "No Content", {"X-Backend": "Auth"})
        case _:
            return web.Response(204, "No Content", {"X-Backend": "Auth"})