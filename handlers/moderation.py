import pyding
from lib import web, utils, config
import logging


clients = utils.TimeoutDict(30)


@pyding.on("http_client")
def client_deny(event: pyding.EventCall, client: web.Client):
    ip = client.address[0]
    if ip not in clients:
        clients[ip] = 0
    clients[ip] += 1

    logging.info(f"New connection from {ip}")
    if clients[ip] > config.get_rate():
        event.cancel()
        logging.info(f"Dropped connection from {ip} ({clients[ip]})")
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
def http_request(event, request: web.Request, client: web.Client, host: str):
    if not request or not request.method or not request.path or ".." in request.path:
        return web.Response(400, "Bad Request", {"X-Backend": "Moderation"})

    logging.info(f"Request for [{request.method}] {request.path}") 
    return


@pyding.on("http_response")
def http_response(event, request: web.Request, response: web.Response):
    logging.info(f"Served [{response.status_code}] [{response.status_message}] for [{request.method}] {request.path}") 
    return
