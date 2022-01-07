import ssl
import pyding
import socket
import logging

from ..config import Config
from datetime import datetime
from urllib.parse import unquote
from space.utils import thread_function

def response(status_code, status_message, headers={}, data=b""):
		status = f"HTTP/1.1 {status_code} {status_message}".encode("utf-8")
		head = b""
		for header in headers:
			head += f"\r\n{header}: {headers[header]}".encode("utf-8")

		output = status
		if head:
			output += head
		output += b"\r\n\r\n"+data

		return output

class Server:
    def __init__(self):
        self.config = Config()
        self.running = False
        self.threads = []
    
    def run(self):
        # Initialize the socket
        logging.info(f"Binding to {self.config.web.host}:{self.config.web.port}")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.config.web.host, self.config.web.port))
        self.socket.listen(1000)
        
        self.running = True

        # Deal with HTTPS and SSL
        if self.config.web.https:
            logging.info("Passing socket to event loop as https")
            self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.context.load_cert_chain(self.config.web.credentials.certificate, self.config.web.credentials.private_key)
            with self.context.wrap_socket(self.socket, server_side=True) as sock:
                self.http_loop(sock)
        else:
            logging.info("Passing socket to event loop as http")
            self.http_loop(self.socket)


    def http_loop(self, sock):
        logging.info("Spinning event loop up.")
        while True:
            try:
                # Accept connection
                conn, addr = sock.accept()
                logging.info(f"Accepted conneciton from {addr}")
                # Route connection to thread
                self.request(self, conn, addr)
            # Ignore SSL errors
            except ssl.SSLError:
                pass
            except KeyboardInterrupt:
                sock.shutdown()
                break
            except Exception as e:
                logging.error(f"Error whilst handling request ({e})")
    
    @thread_function
    def request(self, conn, addr):
        data = b""
        headers = {}

        try:
            while True:
                if b"\r\n\r\n" in data:
                    for line in data.split(b"\n")[1:]:
                        headers[line.split(b": ")[0].decode('utf-8')] = b"".join(line.split(b": ")[1:]).decode('utf-8')
                    if "Content-Length" in headers:
                        body = b"\r\n\r\n".join(data.split(b"\r\n\r\n")[1:])
                        if len(body) >= int(headers["Content-Length"]):
                            break
                    else:
                        break
                new_data = conn.recv(1)
                if not new_data:
                    break
                data += new_data
        
            request = Request(data, acknowledge=datetime.now())
            event = pyding.call("http_request", request=request, connection=conn, address=addr)
            pyding.call("http_response", request=request, resp=event.response.decode('utf-8'))
            
            if event.response:
                conn.send(event.response)

        except Exception as e:
            logging.error(f"Error whilst reading client data ({addr} - {e})")

        conn.close()



class Request(object):
	'''
	This class handles the client-side requests
	'''

	def __init__(self, data: bytes, acknowledge):
		self.acknowledge = acknowledge
		lines = data.split(b"\n")
		if lines[0].endswith(b"\r"):
			lines = data.split(b"\r\n")

		self.method = lines[0].split(b" ")[0].decode('utf-8')
		self.path = lines[0].split(b" ")[1].split(b"?")[0].decode('utf-8')

		self.query_string = {}

		query_string = lines[0].split(b" ")[1].split(b"?")
		if len(query_string) > 1:
			for query_string in query_string[1].split(b"&"):
				string = query_string.split(b"=")
				self.query_string[unquote(string[0].decode('utf-8'))] = unquote(b"".join(string[1:]).decode('utf-8'))

		self.content = b""
		self.headers = {}
		self._hit_switch = False
		self._index = 0
		for line in lines[1:]:
			if not line:
				self._hit_switch = True
				break
			self.headers[line.split(b": ")[0].decode('utf-8')] = b"".join(line.split(b": ")[1:]).decode('utf-8')
			self._index+=1
		self.data = b"\r\n\r\n".join(data.split(b"\r\n\r\n")[1:])


	def append_data(self, data):
		# TODO: Add support for appending data after instanciate
		# This will allow truncate requests to be handled easier.
		pass