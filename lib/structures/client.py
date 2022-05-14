from .request import Request

import pyding
from types import FunctionType, GeneratorType

class Client:
    """
    Client
    ------
    A simple wrapper for socket clients for http processing.
    """
    def __init__(self, connection, address, server):
        self.server = server
        self.connection = connection
        self.address = address
    
    def send_data(self, data):
        self.connection.send(data)
        pyding.call("http_downstream", client=self, data=data)     

    def read_data(self):
        # Init the request
        request = Request()
        # Get the data from the client and only stop if there is no more data or request is done.
        while not request.complete:
            # Recieve data
            new_data = self.connection.recv(1)
            # Break if no data is recieved
            if not new_data:
                break
            # Append new data
            request.append_raw_data(new_data)
        # Process the request
        self.process_data(request)

    def close_connection(self):
        self.connection.close()


    def process_data(self, data):
        if not data:
            self.close_connection()
            return

        event = pyding.call("http_request", request=data, client=self, host=data.headers['Host'] if 'Host' in data.headers else None, first_response=True)
        if event.response:
            pyding.call("http_response", response=event.response, request=data)
            for content in event.response.output():
                # Transfer control over to a handler.
                if isinstance(content, FunctionType):
                    content(client=self, request=data)
                    pyding.call("http_handover", client=self, handler=content)
                    return
                elif isinstance(content, GeneratorType):
                    for data in content:
                        self.send_data(data)
                    break
                # Send data
                self.send_data(content)
        # Since we're done, close the connection.
        self.close_connection()
