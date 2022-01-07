import threading
from time import time

class thread_function:
    def __init__(self, function):
        self.function = function

    def __call__(self, *args):
        self.start_time = time()
        self.thread = threading.Thread(target=self.function, args=args, daemon=True)
        self.thread.start()
        return self

