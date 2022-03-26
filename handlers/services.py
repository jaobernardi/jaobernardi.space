from email.quoprimime import unquote
import pyding
import requests
from lib import web, config, twitter
import logging
from urllib.parse import unquote, urlparse
from random import choices
from string import ascii_letters


def relay_data(url, chunksize=1024):
    req = requests.get(url, stream=True)
    for data in req.iter_content(chunksize):
        yield data


@pyding.on("http_request")
def services_route(event, request: web.Request, client: web.Client):
    
    if "Host" not in request.headers or request.headers["Host"] != "services.jaobernardi.space":
        return

    match request.method, request.path.split("/")[1:] if request.path else "", request.headers:
        case "GET", ["twitter", "video", id]:
            http_status = {
                "status": 301,
                "message": "Permanent Redirect",
                "headers": {
                    "Location": f"/twitter/video/id/{id}"
                }
            }

        case "GET", ["twitter", "video", "url", url], head:
            url = unquote(url)
            parsed_url = urlparse(url)
            if parsed_url.netloc == "video.twimg.com":
                filename = "".join(choices(ascii_letters, k=16))
                http_status = {
                    "status": 200,
                    "message": "Ok",
                    "headers": {
                        "Content-Type": "video/mp4",
                        "Content-Disposition": f"attachment; filename=\"{filename}.mp4\"",
                    }
                }

                output = relay_data(url)
            else:
                failed = open("assets/generic_403.html", "rb")
                output = failed.read()
                failed.close()
                http_status = {
                    "status": 403,
                    "message": "Forbidden",
                    "headers": {
                        "Content-Type": "text/html",
                        "Content-Length": len(output),
                    }
                }
            
        case "GET", ["twitter", "video", "id", id], head:        
            try:
                video_url = twitter.get_video(id)
                
                http_status = {
                    "status": 200,
                    "message": "Ok",
                    "headers": {
                        "Content-Type": "video/mp4",
                        "Content-Disposition": f"attachment; filename=\"{id}.mp4\"",
                    }
                }

                output = relay_data(video_url)
            except:
                failed = open("assets/services_fail.html", "rb")
                output = failed.read()
                failed.close()
        
                http_status = {
                    "status": 500,
                    "message": "Internal Server Error",
                    "headers": {
                        "Content-Type": "text/html",
                        "Content-Length": len(output),
                    }
                }
        case _:
            output = b" "
            http_status = {"status": 403, "message": "Forbidden", "headers": {}}

    return web.Response(http_status['status'], http_status['message'], {"X-Backend": "Services"} | http_status['headers'], output)
