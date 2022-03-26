import json
import pathlib
import pyding
from lib import web, config, html_parsing
import os
import base64
import mimetypes

headers = {"X-Backend": "Content", "Server": "jdspace"}


# TODO: FIX & CLEAN THIS AFTER!!! ok


def load_error(code, **kwargs):
    if f"generic_{code}.html" in os.listdir("assets"):
        error_file = open(f"assets/generic_{code}.html", "rb").read()
    else:
        error_file = open(f"assets/generic_message.html", "rb").read()

    html_error = html_parsing.eval_document(error_file, kwargs | {"code": code})
    return html_error, len(html_error)


@pyding.on("http_request")
def html_route(event, request: web.Request, client: web.Client):
    if "Host" not in request.headers or request.headers["Host"] != "jaobernardi.space":
        return

    # Serve files
    
    path = pathlib.Path("www") / pathlib.Path(request.path.removeprefix("/"))
    
    # Check if file is a path
    if path.is_dir():
        # Set file to index.html
        path = path / pathlib.Path("index.html")

    filename = os.path.basename(path)
    dirname = os.path.dirname(path)

    # Check if requested file is .settings (403 Forbidden)
    if filename == ".settings":
        error_html, error_size = load_error(403, request=request)
        return web.Response(403, "Forbidden", headers | {"Content-Type": "text/html", "Content-Length": error_size}, error_html)


    # Check if there is a '.settings' file in path.
    if ".settings" in os.listdir(dirname):   
        
        settings_path = pathlib.Path(os.path.dirname(path)) / pathlib.Path(".settings")
        path_settings = json.load(open(settings_path))
        
        # Check if filename has an alias
        if "alias" in path_settings and filename in path_settings['alias']:
            path = path.parent / pathlib.Path(path_settings['alias'][filename])
            filename = path_settings['alias'][filename]
        
        # Check if filename is hidden (will return 403 Forbidden)
        if "hidden" in path_settings and filename in path_settings["hidden"]:
            error_html, error_size = load_error(403, request=request)
            return web.Response(403, "Forbidden", headers | {"Content-Type": "text/html", "Content-Length": error_size}, error_html)

        if "require_auth" in path_settings and filename in path_settings["require_auth"]:
            cred = base64.b64encode(config.get_stream_auth().encode("utf-8")).decode("utf-8")
            if "Authorization" not in request.headers or f'Basic {cred}' == request.headers['Authorization']:
                error_html, error_size = load_error(401, request=request)
                return web.Response(401, "Unauthorized", headers | {"WWW-Authenticate": f"Basic realm=\"{path_settings['require_auth'][filename]}\"", "Content-Type": "text/html", "Content-Length": error_size}, error_html)
        if "redirect" in path_settings and filename in path_settings["redirect"]:
            redirect_html, html_size = load_error("Redirecionamento", request=request)
            return web.Response(301, "Moved Permanently", headers | {"Location": path_settings['redirect'][filename], "Content-Type": "text/html", "Content-Length": html_size}, redirect_html)
    
    if not path.exists():
        error_html, error_size = load_error(404, request=request)
        return web.Response(404, "Not Found", headers | {"Content-Type": "text/html", "Content-Length": error_size}, error_html)
    
    try:
        found_file = open(str(path), "rb").read()
        found_file = html_parsing.eval_document(found_file, {"request": request})
        return web.Response(
            200,
            "OK",
            headers | {
                "Content-Type": mimetypes.MimeTypes().guess_type(str(path))[0],
                "Content-Length": len(found_file)
                },
            found_file)
    except:
        error_html, error_size = load_error(500, request=request)
        return web.Response(500, "Internal Server Error", headers | {"Content-Type": "text/html", "Content-Length": error_size}, error_html)