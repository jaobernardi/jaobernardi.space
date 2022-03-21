import pyding
from lib import web, config, html_parsing

headers = {"X-Backend": "Fallback", "Server": "jdspace"}

@pyding.on("http_request", priority=float("-inf"))
def fallback_route(event, request: web.Request, client: web.Client):
    if not event.response:
        fallback_file = open("www/fallback.html", "rb")
        fallback_page = html_parsing.eval_document(fallback_file.read(), {"request": request})
        fallback_file.close()

        return web.Response(503, "Service Unavailable", headers={"Content-Type": "text/html", "Content-Length": len(fallback_page)} | headers, data=fallback_page)