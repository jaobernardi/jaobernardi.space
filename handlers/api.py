from email import message
import json
from lib import web
import pyding
import base64
import hashlib
import hmac

@pyding.on("http_client")
def client_deny(event: pyding.EventCall, client):
    return

@pyding.on("http_request")
def api_route(event, request: web.Request):
    match request.path.split("/")[1:]:
        case ["relay"]:
            pyding.call("relay_broadcast", message=request.raw_data)
            out = {"status": 200, "http_message": "OK", "message": "Relayed."}

        case ["acervo", *extra]:
            out = {"status": 501, "http_message": "OK", "message": "Not Implemented."}
       
        case _:
            out = {"status": 404, "http_message": "Not Found",  "message": "Method not found"}
    
    
    out_parsed = json.dumps(out).encode()
    return web.Response(out['status'], out['http_message'], {"Server": "jdspace", "Content-Type": "application/json", "Content-Length": len(out_parsed)}, out_parsed)
