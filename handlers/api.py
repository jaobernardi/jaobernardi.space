from email import message
import json
from lib import web, config, relay
import pyding
import base64
import hashlib
import hmac
import os


@pyding.on("http_client")
def client_deny(event: pyding.EventCall, client):
    return

@pyding.on("http_request")
def api_route(event, request: web.Request):
    output = {}
    match request.path.split("/")[1:] if request.path else "":
        case ["webhooks", "twitter"]:
            if "crc_token" in request.query_string:
                sha256_hash_digest = hmac.new(config.get_user_token().encode("utf-8"), msg=request.query_string['crc_token'].encode("utf-8"), digestmod=hashlib.sha256).digest()
                output = {"response_token": 'sha256=' + base64.b64encode(sha256_hash_digest).decode("utf-8")}
            out = {"status": 200, "http_message": "OK"}
            pyding.call("relay_broadcast", message=request.raw_data)
        
        case ["webhooks", "twitter", "stream"]:
            def add_connection(client, request):
                pyding.call("relay_add", client=client, request=request)
            
            return web.Response(200, "OK", {"Server": "jdspace"}, add_connection)

        case ["relay"]:
            out = {"status": 200, "http_message": "OK"}
            output = {"relayed": True}
            
            
        case ["acervo", *extra]:
            out = {"status": 501, "http_message": "OK"}
       
        case _:
            out = {"status": 404, "http_message": "Not Found"}

    
    
    output = json.dumps(output).encode()
    return web.Response(out['status'], out['http_message'], {"Server": "jdspace", "Content-Type": "application/json", "Content-Length": len(output)}, output)
