import pyding
import requests
from lib import web, config, twitter
import logging

headers = {"X-Backend": "Services", "Server": "jdspace"}

@pyding.on("http_request")
def services_route(event, request: web.Request, client: web.Client):
    
    if "Host" not in request.headers or request.headers["Host"] != "services.jaobernardi.space":
        return

    match request.method, request.path.split("/")[1:] if request.path else "", request.headers:
        case method, ["twitter", "video", id, *extra], headers:
            def send_data(url, chunksize=1024):
                req = requests.get(video_url, stream=True)
                for data in req.iter_content(chunksize):
                    yield data
        

            try:
                chunksize = 1024
            
                if "chunksize" in request.query_string:
                    chunksize = int(request.query_string['chunksize'])
                    if chunksize > 1024:
                        chunksize = 1024
                video_url = twitter.get_video(id)
                

                http_status = {
                    "status": 200,
                    "message": "Ok",
                    "headers": {
                        "Content-Type": "video/mp4",
                        "Content-Disposition": f"attachment; filename=\"{id}.mp4\""
                    }
                }

                output = send_data(video_url, chunksize)
            except:
                failed = open("www/services_fail.html", "rb")
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
            output = b""
            http_status = {"status": 403, "message": "Forbidden", "headers": {}}

    return web.Response(http_status['status'], http_status['message'], headers | http_status['headers'], output)
