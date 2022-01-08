from space import web, Config
import logging
import pyding
import os
import importlib


server_modules = []

logging.basicConfig(level=logging.INFO)

config = Config()


@pyding.on("http_request", priority=float("-inf"))
def fallback_server(event, request, connection, address):
    error_file = open("web/error.html", "rb")
    error_contents = error_file.read()    

    if "Host" in request.headers and request.headers["Host"] == config.web.scopes.home:
        default_headers = {"Server": "jspaces/1.0"}
        path = os.path.join("web/", request.path.removeprefix("/"))

        if ".." in path:
            error_parsed = web.eval_document(error_contents, {"request": request, "address": address, "code": 403, "text": "Unauthorized"}).encode("utf-8")
            return web.response(403, 'Unauthorized', default_headers, error_parsed)

        if os.path.exists(path):
            # detect file
            if os.path.isfile(path):
                filename = path
            elif os.path.exists(os.path.join(path, 'index.html')):
                filename = os.path.join(path, "index.html")
            else:
                error_parsed = web.eval_document(error_contents, {"request": request, "address": address, "code": 404, "text": "Not Found"}).encode("utf-8")
                return web.response(404, 'Not Found', default_headers, error_parsed)
        else:
            # not found response
            error_parsed = web.eval_document(error_contents, {"request": request, "address": address, "code": 404, "text": "Not Found"}).encode("utf-8")
            return web.response(404, 'Not Found', default_headers, error_parsed)
        
        data = open(filename, 'rb').read()
        prefix = os.path.basename(filename).split(".")[-1]
        if prefix in config.mime_types.mime_types:
            default_headers['Content-Type'] = config.mime_types[prefix]
        data = web.eval_document(data, {"request": request, "address": address}).encode("utf-8")
        
        return web.response(
            200,
            'OK', 
            default_headers|{
                'Content-Length': len(data),
            },
            data
        )


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