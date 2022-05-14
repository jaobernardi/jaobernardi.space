from lib import structures
import pyding


@pyding.on("http_request")
def placeholder_handler(*args, **kwargs):
    return structures.Response.ok(b"Hello, world!", "text/plain")
