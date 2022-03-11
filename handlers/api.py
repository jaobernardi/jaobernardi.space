from email import message
import json
from lib import web, config, relay
import pyding
import base64
import hashlib
import hmac
import os



def add_connection(client, request):
    pyding.call("relay_add", client=client, request=request)

@pyding.on("http_request")
def api_route(event, request: web.Request):
    output = {}
    match request.method, request.path.split("/")[1:] if request.path else "", request.headers:
        case "GET", ["webhooks", "twitter"], headers:
            # Do the CRC challange for twitter
            if "crc_token" in request.query_string:
                # Do the hash things
                sha256_hash_digest = hmac.new(
                    config.get_user_token().encode("utf-8"),
                    digestmod=hashlib.sha256)\
                    .digest()
                # Return final token
                crc = 'sha256=' + base64.b64encode(sha256_hash_digest).decode("utf-8")
                output = {
                    "response_token": crc
                }
        case "POST", ["webhooks", "twitter"], {"X-Twitter-Webhooks-Signature": twitter_signature, **headers}:
            # Check twitter headers
            sha256_hash_digest = hmac.new(
                config.get_user_token().encode("utf-8"),
                msg=request.data,
                digestmod=hashlib.sha256)\
                .digest()
            
            signature = b'sha256=' + base64.b64encode(sha256_hash_digest)
            print(signature, twitter_signature)
            if signature == twitter_signature:
                http_status = {"status": 200, "message": "OK"}
                # Relay data
                if request.data:
                    pyding.call("relay_broadcast", message=request.data)
            else:
                http_status = {"status": 403, "message": "Forbidden"}

        case method, ["webhooks", "twitter", "stream"], headers:
            # Return a response with a handover handler function.
            return web.Response(200, "OK", {"Server": "jdspace"}, add_connection)

        case "POST", ["relay"], headers:
            http_status = {"status": 200, "message": "OK"}
            output = {"relayed": True}
             
        case "POST", ["acervo", *extra], headers:
            http_status = {"status": 501, "message": "OK"}

        case _:
            http_status = {"status": 403, "message": "Forbidden"}

    
    
    output = json.dumps(output).encode()
    return web.Response(http_status['status'], http_status['message'], {"Server": "jdspace", "Content-Type": "application/json", "Content-Length": len(output)}, output)
