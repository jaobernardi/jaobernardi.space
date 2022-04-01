import os
import time


def load_handlers():
    for handler in os.listdir("handlers"):
        if handler.endswith(".py"):
            __import__("handlers."+handler.removesuffix(".py"))


class TimeoutList:
    def __init__(self, ttl):
        self._store = {}
        self.ttl = ttl
    
    def check(self):
        for item in list(self._store):
            if self._store[item]['expiry'] <= time.time():
                self._store.pop(item)

    def append(self, item):
        self.check()
        self._store[item] = {"expiry": time.time()+self.ttl}    

    def __contains__(self, item):
        self.check()
        return item in self._store

    def __repr__(self):
        self.check()
        return list(self._store).__repr__()

    def __iter__(self):
        self.check()
        return self._store.__iter__()


class TimeoutDict:
    def __init__(self, ttl):
        self._store = {}
        self.ttl = ttl
    
    def check(self):
        for item in list(self._store):
            if self._store[item]['expiry'] <= time.time():
                self._store.pop(item)

    def __setitem__(self, item, value):
        self.check()
        self._store[item] = {"expiry": time.time()+self.ttl, "value": value}    

    def __getitem__(self, item):
        self.check()
        if item in self._store:
            return self._store[item]['value']

    def __contains__(self, item):
        self.check()
        return item in self._store

    def __repr__(self):
        self.check()
        return list(self._store).__repr__()

    def __iter__(self):
        self.check()
        return self._store.__iter__()

