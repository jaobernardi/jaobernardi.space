import pyding
from lib import web
import logging


@pyding.on("http_client")
def client_deny(event: pyding.EventCall, client: web.Client):
    logging.info(f"New connection from {client.address[0]}")
    return


@pyding.on("http_downstream")
def client_handover(event: pyding.EventCall, client: web.Client, data: bytes):
    logging.debug(f"Sending data to {client.address[0]}")
    return


@pyding.on("http_handover")
def client_handover(event: pyding.EventCall, client: web.Client, handler):
    logging.info(f"Connection control flow for {client.address[0]} changed.")
    return


@pyding.on("http_request", priority=float("inf"))
def http_request(event, request: web.Request, client: web.Client):
    logging.info(f"Request for [{request.method}] {request.path}") 
    return


@pyding.on("http_response")
def http_response(event, request: web.Request, response: web.Response):
    # TODO: Support for relative paths
    if ".." in request.path:
        return web.Response(403, "Forbidden", {"X-Backend": "Moderation"})

    logging.info(f"Served [{response.status_code}] [{response.status_message}] for [{request.method}] {request.path}") 
    return
