from urllib.parse import quote
import pyding
from lib import web, config, utils
import logging
from random import choices
from string import ascii_letters
from pyotp.totp import TOTP


states = utils.TimeoutList(60)
totp = TOTP(config.get_otp)


@pyding.on("http_request", host=config.get_hosts()['auth']['url'])
def auth_handler(event, request: web.Request, client: web.Client, host: str):
    match request.method, request.path.split("/")[1:], request.query_string:
        case "GET", ["spotify", "authenticate"], {"otp": otp, **_params} if otp == totp.now():
            state = choices(ascii_letters, k=16)
            state = "".join(state)  
            states.append(state)         
            return web.Response.redirect(
                (f"https://accounts.spotify.com/authorize?"
                f"state={state}"
                "&response_type=code"
                f"&client_id={config.get_spotify_client_id()}"
                f"&scope=user-read-private user-read-email user-modify-playback-state user-read-currently-playing user-read-playback-state streaming"
                f"&redirect_uri=https://{config.get_hosts()['api']['url']}/spotify/callback"),
                {"X-Backend": "Auth"}
            )

        case "GET", ["spotify", "callback"], {"code": code, "state": state, **_params} if state in states:
            asset = open(f"assets/spotify/auth_success.html", "rb")
            asset = asset.read()
            content_type = "text/html"

            return web.Response.ok(asset, content_type, {"X-Backend": "Auth"})

        case "GET", ["spotify", "callback"], _params:
            asset = open(f"assets/spotify/auth_fail.html", "rb")
            asset = asset.read()
            content_type = "text/html"

            return web.Response.ok(asset, content_type, {"X-Backend": "Auth"})

        case "POST", ["users", "session"], _params:
            response = web.Response()
            response.create_session(domain="jaobernardi.localhost")
            return response

        case "GET", ["users", "session"] | ["login"], _params:
            asset = open(f"assets/pages/login.html", "rb")
            asset = asset.read()
            content_type = "text/html"

            return web.Response.ok(asset, content_type, {"X-Backend": "Auth"})
        case _:
            return web.Response(204, "No Content", {"X-Backend": "Auth"})