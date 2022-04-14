import json
import pathlib
import pyding
from lib import web, config, html_parsing
import os
import base64
import mimetypes



# TODO: FIX & CLEAN THIS AFTER!!! ok


def load_error(code, **kwargs):
    if f"generic_{code}.html" in os.listdir("assets/pages/"):
        error_file = open(f"assets/pages/generic_{code}.html", "rb").read()
    else:
        error_file = open(f"assets/pages/generic_message.html", "rb").read()

    html_error = html_parsing.eval_document(error_file, kwargs | {"code": code})
    return html_error, len(html_error)


@pyding.on("http_request", host=config.get_hosts()['home']['url'])
def html_route(event, request: web.Request, client: web.Client, host: str):
    # Serve files
    response = web.Response(204, "No Content")

    path = pathlib.Path(config.get_root()) / pathlib.Path(request.path.removeprefix("/"))
    
    # Check if file is a path
    if path.is_dir():
        # Set file to index.html
        path = path / pathlib.Path("index.html")

    filename = os.path.basename(path)
    dirname = os.path.dirname(path)

    # Check if requested file is .settings (403 Forbidden)
    if filename == ".settings":
        error_html, error_size = load_error(403, request=request)
        return response.update(403, "Forbidden", {"X-Backend": "Content", "Content-Type": "text/html", "Content-Length": error_size}, error_html)


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
            return response.update(403, "Forbidden", {"X-Backend": "Content", "Content-Type": "text/html", "Content-Length": error_size}, error_html)

        if "require_auth" in path_settings and filename in path_settings["require_auth"]:
            cred = base64.b64encode(config.get_stream_auth().encode("utf-8")).decode("utf-8")
            if "Authorization" not in request.headers or f'Basic {cred}' == request.headers['Authorization']:
                error_html, error_size = load_error(401, request=request)
                return response.update(401, "Unauthorized", {"X-Backend": "Content", "WWW-Authenticate": f"Basic realm=\"{path_settings['require_auth'][filename]}\"", "Content-Type": "text/html", "Content-Length": error_size}, error_html)
        if "redirect" in path_settings and filename in path_settings["redirect"]:
            redirect_html, html_size = load_error("Redirecionamento", request=request)
            return response.update(301, "Moved Permanently", {"X-Backend": "Content", "Location": path_settings['redirect'][filename], "Content-Type": "text/html", "Content-Length": html_size}, redirect_html)
    
    if not path.exists():
        error_html, error_size = load_error(404, request=request)
        return response.update(404, "Not Found", {"X-Backend": "Content", "Content-Type": "text/html", "Content-Length": error_size}, error_html)
    
    try:
        found_file = open(str(path), "rb").read()
        found_file = html_parsing.eval_document(found_file, {"request": request, "response": response})
        return response.update(
            200,
            "OK",
            {"X-Backend": "Content", 
                "Content-Type": mimetypes.MimeTypes().guess_type(str(path))[0],
                "Content-Length": len(found_file)
                },
            found_file)
    except:
        error_html, error_size = load_error(500, request=request)
        return response.update(500, "Internal Server Error", {"X-Backend": "Content", "Content-Type": "text/html", "Content-Length": error_size}, error_html)