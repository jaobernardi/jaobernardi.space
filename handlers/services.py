import pyding
import requests
from lib import web, config, twitter
import logging


@pyding.on("http_request")
def services_route(event, request: web.Request):
    
    if "Host" not in request.headers or request.headers["Host"] != "services.jaobernardi.space":
        return

    match request.method, request.path.split("/")[1:] if request.path else "", request.headers:
        case method, ["twitter", "video", id, *extra], headers:
            def send_data(req):
                for data in req.iter_content(1024):
                    yield data
            video_url = twitter.get_video(id)
            try:
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
            except:
                failed = open("www/services_fail.html", "rb")
                output = failed.read()
                failed.close()
        
                http_status = {
                    "status": 500,
                    "message": "Internal Server Error",
                    "headers": {
                        "Content-Type": "text/html",
                        "Content-Length": len(failed),
                    }
                }
        case _:
            output = b""
            http_status = {"status": 403, "message": "Forbidden", "headers": {}}

    return web.Response(http_status['status'], http_status['message'], {"Server": "jdspace"} | http_status['headers'], output)
