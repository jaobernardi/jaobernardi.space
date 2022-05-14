from types import GeneratorType
from .. import config

class Response:
    """
    Response
    --------
    A simple http response parsing.
    """
    def __init__(self, status_code=200, status_message="OK", headers={}, data=b" "):
        self.status_code = status_code
        self.status_message = status_message
        self.headers = headers | {"Connection": "close"} | config.get_headers()
        self.data = data
        self.cookies = {}

    def destroy_cookie(self, name):
        """Sends a Set-Cookie header to delete a cookie on client's side.
        Args:
            name (string): Cookie's name
        """
        self.cookies[name] = {
            'value': '$',
            'attr': {
                'Expires': 'Thu, 01 Jan 1970 00:00:00 GMT',
            }
        }

    def remove_cookie(self, name):
        """Remove the cookie from Response's cookie dict
        Args:
            name (name): Cookie's name
        """
        self.cookies.pop(name)


    def add_cookie(self, name, value, expires=None, secure=False, httponly=False, domain=None, path=None, maxage=None, extra: dict = {}):
        """Add a Set-Cookie header to response
        Args:
            name (str): Cookie's name
            value (str): Cookie value
            expires (str, optional): Expire attribute of Set-Cookie. Defaults to None.
            secure (bool, optional): Secure. Defaults to False.
            httponly (bool, optional): HttpOnly. Defaults to False.
            domain (str, optional): Domain. Defaults to None.
            path (str, optional): Path. Defaults to None.
            maxage (str, optional): Max-Age. Defaults to None.
            extra (dict, optional): Extra attributes. Defaults to {}.
        """
        self.cookies[name] = {
            'value': value,
            'attr': {
                'Expires': expires,
                'Secure': secure,
                'HttpOnly': httponly,
                'Domain': domain,
                'Path': path, 
                'Max-Age': maxage
            } | extra
        }


    def update(self, status_code=200, status_message="OK", headers={}, data=b" "):
        self.status_code = status_code
        self.status_message = status_message
        self.headers = headers | {"Server": "jdspace", "Connection": "close"}
        self.data = data
        return self

    @classmethod
    def redirect(cls, location, headers={}):
        return cls(
            301,
            "Permanent Redirect",
            headers | {"Location": location}
        )

    @classmethod
    def ok(cls, data, content_type, headers={}):
        return cls(
            200,
            "OK",
            headers | {"Content-Type": content_type, "Content-Length": len(data)},
            data
        )

    @classmethod
    def not_found(cls, data, content_type, headers={}):
        return cls(
            404,
            "Not Found",
            headers | {"Content-Type": content_type, "Content-Length": len(data)},
            data
        )

    def output(self):
        yield f"HTTP/1.1 {self.status_code} {self.status_message}".encode("utf-8")
        for header_name, header_value in self.headers.items():
            yield f"\r\n{header_name}: {header_value}".encode("utf-8")

        for cookie_name, cookie_data in self.cookies.items():
            append = ""
            for cookie_attr, attr_value in cookie_data['attr'].items():
                
                if isinstance(attr_value, str):
                    append += f"; {cookie_attr}={attr_value}"
                elif attr_value:
                    append += "; "+cookie_attr
                
            yield f"\r\nSet-Cookie: {cookie_name}={cookie_data['value']}{append}".encode("utf-8")

        if self.data:
            yield b"\r\n\r\n"
            if isinstance(self.data, GeneratorType):
                for i in self.data:
                    yield i
            else:
                yield self.data
