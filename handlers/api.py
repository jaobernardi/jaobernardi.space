from email import message
import json
from lib import web, config, relay
import pyding
import base64
import hashlib
import hmac
import os

last_crc = None

def add_connection(client, request):
    pyding.call("relay_add", client=client, request=request)

@pyding.on("http_request")
def api_route(event, request: web.Request):
    output = {}
    match request.path.split("/")[1:] if request.path else "":
        case ["webhooks", "twitter"]:
            # Verify Twitter Headers
            print(request.raw_data)
        


            # Do the CRC challange for twitter
            if "crc_token" in request.query_string:
                # Do the hash things
                sha256_hash_digest = hmac.new(
                    config.get_user_token().encode("utf-8"),
                    msg=request.query_string['crc_token'].encode("utf-8"),
                    digestmod=hashlib.sha256)\
                    .digest()
                # Return final token
                last_crc = 'sha256=' + base64.b64encode(sha256_hash_digest).decode("utf-8")
                output = {
                    "response_token": last_crc
                }
                print(output)
            # Return 200 OK
            http_status = {"status": 200, "message": "OK"}
            # Relay data
            if request.data:
                pyding.call("relay_broadcast", message=request.data)

        case ["webhooks", "twitter", "stream"]:
            # Return a response with a handover handler function.
            return web.Response(200, "OK", {"Server": "jdspace"}, add_connection)

        case ["relay"]:
            http_status = {"status": 200, "message": "OK"}
            output = {"relayed": True}
            
            
        case ["acervo", *extra]:
            http_status = {"status": 501, "message": "OK"}
       
        case _:
            http_status = {"status": 404, "message": "Not Found"}

    
    
    output = json.dumps(output).encode()
    return web.Response(http_status['status'], http_status['message'], {"Server": "jdspace", "Content-Type": "application/json", "Content-Length": len(output)}, output)
