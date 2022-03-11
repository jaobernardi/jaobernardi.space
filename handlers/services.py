import pyding
import requests
from lib import web, config, twitter
import logging


@pyding.on("http_request")
def services_route(event, request: web.Request):
    
    if "Host" not in request.headers or request.headers["Host"] != "services.jaobernardi.space":
        return
    if "User-Agent" in request.headers and "Twitterbot" in request.headers["User-Agent"]:
        logging.info("Serving data for Twitterbot")
        data = ("<!DOCTYPE html>"
        '<html lang="en">'
        '<head>'
            '<meta name="twitter:card" content="summary" />'
            '<meta name="twitter:site" content="@jaobernard" />'
            '<meta name="twitter:title" content="JDSpace | Serviços" />'
            '<meta name="twitter:image" content="https://jaobernardi.space/jdspace.png" />'
        "</head>"
        "<body>" 
        "</body>"
        "</html>").encode("utf-8")
        return web.Response(200, "OK", {"Server": "jdspace", "Content-Type": "text/html", "Content-Length": len(data)}, data)
    
    match request.method, request.path.split("/")[1:] if request.path else "", request.headers:
        case method, ["twitter", "video", id], headers:
            def send_data(req):
                for data in req.iter_content(1024):
                    yield data
            video_url = twitter.get_video(id)
            req = requests.get(video_url, stream=True)

            http_status = {
                "status": 200,
                "message": "Ok",
                "headers": {
                    "Content-Type": req.headers['Content-Type'],
                    "Content-Length": req.headers['Content-Length'],
                    "Content-Disposition": f"attachment; filename=\"{id}.mp4\""
                }
            }

            output = send_data(req)
        case _:
            output = b""
            http_status = {"status": 403, "message": "Forbidden", "headers": {}}

    return web.Response(http_status['status'], http_status['message'], {"Server": "jdspace"} | http_status['headers'], output)
