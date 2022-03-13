from email import message
from email.mime import base
import json
from lib import web, config, relay
import pyding
import base64
import hashlib
import hmac
import os



def handover_connection(client, request):
    pyding.call("relay_add", client=client, request=request)


@pyding.on("http_request")
def api_route(event, request: web.Request, client: web.Client):
    
    if "Host" not in request.headers or request.headers["Host"] != "api.jaobernardi.space":
        return

    output = {}
    match request.method, request.path.split("/")[1:] if request.path else "", request.headers:
        
        case "GET", ["webhooks", "twitter"], headers:
            http_status = {"status": 403, "message": "Forbidden", "headers": {}}
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
                http_status = {"status": 200, "message": "OK", "headers": {}}
            print(output)
        case "POST", ["webhooks", "twitter"], {"X-Twitter-Webhooks-Signature": twitter_signature, **headers}:
            # Check twitter headers
            sha256_hash_digest = hmac.new(
                config.get_user_token().encode("utf-8"),
                msg=request.data,
                digestmod=hashlib.sha256)\
                .digest()            
            signature = 'sha256=' + base64.b64encode(sha256_hash_digest).decode("utf-8")

            if signature == twitter_signature:
                http_status = {"status": 200, "message": "OK", "headers": {}}
                # Relay data
                if request.data:
                    pyding.call("relay_broadcast", message=request.data)
            else:
                http_status = {"status": 403, "message": "Forbidden", "headers": {}}


        case "GET", ["webhooks", "twitter", "stream"], {"Authorization": auth, **headers}:
            cred = base64.b64encode(config.get_stream_auth().encode("utf-8")).decode("utf-8")
            if auth == f"Basic {cred}":
                # Return a response with a handover handler function.
                return web.Response(200, "OK", {"Server": "jdspace", "Content-Type": "application/stream+json"}, handover_connection)
            http_status = {"status": 401, "message": "Unauthorized", "headers": {}}


        case "GET", ["webhooks", "twitter", "stream"], headers:
            http_status = {"status": 401, "message": "Unauthorized", "headers": {"WWW-Authenticate": "Basic realm=\"Twitter webhook data stream\""}}


        case "POST", ["acervo", *extra], headers:
            http_status = {"status": 501, "message": "OK", "headers": {}}


        case _:
            http_status = {"status": 403, "message": "Forbidden", "headers": {}}

    
    
    output = json.dumps(output).encode()
    print(http_status['status'], http_status['message'], {"Server": "jdspace", "Content-Type": "application/json", "Content-Length": len(output)} | http_status['headers'], output)
    return web.Response(http_status['status'], http_status['message'], {"Server": "jdspace", "Content-Type": "application/json", "Content-Length": len(output)} | http_status['headers'], output)
