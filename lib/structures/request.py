from urllib.parse import unquote

class Request:
    """
    Response
    --------
    A simple http response forgery.
    """
    def __init__(self, raw_data: bytes = b""):
        self.raw_data = raw_data
        self.parse_raw_data()

    @staticmethod
    def parse_query_string(query_string):
        if isinstance(query_string, bytes):
            query_string = query_string.decode("utf-8")
        return {unquote(k): unquote(v) for k, v in [i.split("=") for i in query_string.split("&") if "=" in i]}

    def parse_raw_data(self):
        self.method = None
        self.path = None
        self.query_string = {}
        self.headers = {}
        self.data = None
        self.complete = False
        index = 0
        head, *body = self.raw_data.split(b"\r\n\r\n")
        # TODO: Rewrite this bit
        for line in head.split(b"\r\n"):
            line = line.decode("utf-8")
            if " " in line and index == 0:
                self.method, *other = line.split(" ")
                self.path = other[0] if other else ""
                self.path = self.path.split("?")[0]
                if "?" in other[0] and "=" in other[0]:
                    self.query_string = "?".join(other[0].split("?")[1:])
                                       
                    self.query_string = self.parse_query_string(self.query_string)

            elif index > 0:
                line = line.removesuffix("\r\n").split(": ")
                if line[0]:
                    self.headers[line[0]] = "".join(line[1:])
            index += 1
        if "Content-Length" in self.headers and body:
            body = [body] if not isinstance(body, list) else body
            body = b"\r\n\r\n".join(body)
            if "Content-Type" in self.headers and self.headers['Content-Type'] == 'application/x-www-form-urlencoded':
                self.data = self.parse_query_string(body)
            else:
                self.data = body  
            if len(body) >= int(self.headers["Content-Length"]):
                self.complete = True

        elif b"\r\n\r\n" in self.raw_data:
            self.complete = True

    @property
    def cookies(self):
        if "Cookie" in self.headers:
            return {k: v for k,v in [i.split("=") for i in self.headers['Cookie'].split("; ")]}
        return {}

    def append_raw_data(self, raw_data):
        self.raw_data += raw_data
        self.parse_raw_data()