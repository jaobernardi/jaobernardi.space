from space import web
import logging
import pyding
import os
import importlib


server_modules = []

logging.basicConfig(level=logging.INFO)

@pyding.on("http_request", priority=float("-inf"))
def fallback_server(event, request, connection, address):
    file = open("web/index.htm", "rb")
    contents = file.read()
    try:
        parsed = web.eval_document(contents, {"request": request, "address": address}).encode("utf-8")
        return web.response(200, 'OK', {'Server': 'jaobernardi/backend'}, parsed)
    except:
        logging.error("Failed to meet demands.")
        file = open("web/error.html", "rb")
        contents = file.read()
        parsed = web.eval_document(contents, {"request": request, "address": address, "code": 500, "text": "Internal Server Error"}).encode("utf-8")
        return web.response(500, 'Internal Server Error', {'Server': 'jaobernardi/backend'}, parsed)


def load_servers():
    for handle in os.listdir("servers"):
        if handle.endswith(".py"):            
            handle = __import__("servers."+handle.removesuffix(".py"))
            server_modules.append(handle)


def main():
    load_servers()
    server = web.Server()
    server.run()
    

if __name__ == "__main__":
    main()