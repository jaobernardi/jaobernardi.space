import json
from lib import web
import pyding


@pyding.on("http_request")
def default_route(event, request):
    out = {"status": "Ok", "message": "Hello world!", "request": {"path": request.path, "query_string": request.query_string, "data": request.data.decode("utf-8")}}
    out = json.dumps(out).encode()
    return web.Response(200, "OK", {"Server": "jdspace", "Content-Type": "application/json", "Content-Length": len(out)}, out)