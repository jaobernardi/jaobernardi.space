import pyding
from lib import web, config
from os import path


@pyding.on("http_request", priority=float("inf"))
def html_route(event, request: web.Request):
    print("html")
    if "Host" not in request.headers or request.headers["Host"] != "jaobernardi.space":
        return
    
