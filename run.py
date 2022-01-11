from space import web, Config
import logging
import pyding
import os
import importlib


server_modules = []

logging.basicConfig(level=logging.DEBUG)

config = Config()


@pyding.on("http_request", priority=float("-inf"))
def fallback_server(event, request, connection, address):
    error_file = open("web/error.html", "rb")
    error_contents = error_file.read()    
    default_headers = {"Server": "jspaces/1.0", "Connection": "keep-alive", "Accept-Ranges": "bytes"}

    if "Host" in request.headers and request.headers["Host"] == config.web.scopes.home or True:        
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
        
        data = open(filename, 'rb')
        # if "Range" in request.headers:
        #     range = [int(i) for i in request.headers["Range"].split("-")[0:1]]

        prefix = os.path.basename(filename).split(".")[-1]

        if prefix in config.mime_types:
            default_headers['Content-Type'] = config.mime_types[prefix]
        size = os.path.getsize(filename)

        if "Range" in request.headers and config.web.experimental.ranges:
            range = request.headers["Range"].split("=")[-1]
            ranges = []
            
            for r in range.split(", "):
                r = [int(i) if i else None for i in r.split("-")]
                ranges.append(r)
            


            output = []

            for range in ranges:
                #[0, 0]
                match range:
                    case [a, None]: # 0 - 
                        print(1, a)
                        data.seek(a)
                        data = data.read()
                        output.append({"range": f"bytes {a}-{size-a}/*","headers": f"--jspacewall\nContent-Type: {config.mime_types[prefix]}\nContent-Range: bytes {a}-{size-a}/*\n\n", "data": data})
                    
                    case [a, b]:    # 0 - 1000
                        print(2, a, b)
                        if not a:
                            a = 0
                        data.seek(a)
                        data = data.read(b-a+1)
                        output.append({"range": f"bytes {a}-{b}/*", "headers": f"--jspacewall\nContent-Type: {config.mime_types[prefix]}\nContent-Range: bytes {a}-{b}/*\n\n", "data": data})
            
            return web.response(
                206,
                'Partial Content', 
                default_headers|{
                    'Content-Range': output[0]['range'],
                    'Content-Length': len(output[0]['data']),
                },
                output[0]['data']
            )
        else:
            data = data.read()
        
        if prefix in ["html", "htm"]:
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