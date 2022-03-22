import json
import pathlib
import pyding
from lib import web, config, html_parsing
import os
import mimetypes

headers = {"X-Backend": "Content", "Server": "jdspace"}

@pyding.on("http_request", priority=float("inf"))
def html_route(event, request: web.Request, client: web.Client):
    if "Host" not in request.headers or request.headers["Host"] != "jaobernardi.space":
        return

    if request.path.endswith("jdspace.png"):
        jdspace_logo = open("assets/jdspace.png", "rb")
        jdspace_logo = jdspace_logo.read()
        return web.Response(
            200,
            "OK",
            {
            "Content-Type": "image/png",
            "Content-Length": len(jdspace_logo)
            } | headers,
        jdspace_logo
        )

    elif request.path.endswith("archive.png"):
        archive_logo = open("assets/archive.png", "rb")
        archive_logo = archive_logo.read()
        return web.Response(
            200,
            "OK",
            {
                "Content-Type": "image/png",
                "Content-Length": len(archive_logo)
            } | headers,
        archive_logo
        )
    
    path = pathlib.Path("www") / pathlib.Path(request.path.removeprefix("/"))
    if path.is_dir():
        path = path / pathlib.Path("index.html")
    
    if not path.exists():
        not_found_file = open("assets/generic_404.html", "rb").read()
        not_found_file = html_parsing.eval_document(not_found_file, {"request": request})
        return web.Response(404, "Not Found", headers | {"Content-Type": "text/html", "Content-Length": len(not_found_file)}, not_found_file)
    
    if ".settings" in os.listdir(os.path.dirname(path)):
        settings_path = pathlib.Path(os.path.dirname(path)) / pathlib.Path(".settings")
        path_settings = json.load(open(settings_path))
        
        if "hidden" in path_settings and os.path.basename(path) in path_settings["hidden"]:
            forbidden_file = open("assets/generic_403.html", "rb").read()
            forbidden_file = html_parsing.eval_document(forbidden_file, {"request": request})
            return web.Response(403, "Forbidden", headers | {"Content-Type": "text/html", "Content-Length": len(forbidden_file)}, forbidden_file)


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