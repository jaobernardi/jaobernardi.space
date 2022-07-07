from pyding import on


@on("https_request", path="/", host='')
def home_router(event, server, request, response):
    return response.send_file("file")