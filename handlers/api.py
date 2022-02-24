import json
from lib import web
import pyding


@pyding.on("http_request")
def api_route(event, request):
    match request.path.split("/")[1:] if request.path else "":
        case ["ping"]:
            out = {"status": 200, "http_message": "OK", "message": "You've reached the testing page."}

        case ["acervo", *extra]:
            out = {"status": 501, "http_message": "OK", "message": "Not Implemented."}
       
        case _:
            out = {"status": 404, "http_message": "Not Found",  "message": "Method not found"}
    
    
    out_parsed = json.dumps(out).encode()
    return web.Response(out['status'], out['http_message'], {"Server": "jdspace", "Content-Type": "application/json", "Content-Length": len(out_parsed)}, out_parsed)