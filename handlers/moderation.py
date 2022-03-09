import pyding
from lib import web
import logging

@pyding.on("http_client")
def client_deny(event: pyding.EventCall, client: web.Client):
    logging.info(f"New connection from {client.address[0]}")
    return


@pyding.on("http_handover")
def client_handover(event: pyding.EventCall, client: web.Client, handover):
    logging.info(f"Connection handover for {client.address[0]}")
    return


@pyding.on("http_downstream")
def client_handover(event: pyding.EventCall, client: web.Client, data: bytes):
    logging.debug(f"Sending data to {client.address[0]}")
    return


@pyding.on("http_request", priority=float("inf"))
def api_route(event, request: web.Request):
    logging.info(f"Request for [{request.method}] {request.path}") 
    return
