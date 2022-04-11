import os
import time
from string import ascii_letters
from random import choices
import inspect


def load_handlers():
    for handler in os.listdir("handlers"):
        if handler.endswith(".py"):
            __import__("handlers."+handler.removesuffix(".py"))


def random_string(length=16):
    charset = ascii_letters + "".join([str(i) for i in range(10)])
    return "".join(choices(charset, k=length))



class RequireOneArg:
    def __init__(self, func):
        self.func = func
    
    def __repr__(self) -> str:
        return self.func.__repr__()

    def __call__(self, *args, **kwargs):
        required_args = list(inspect.signature(self.func).parameters)
        if not args and not kwargs:
            raise ValueError(f'Missing {" or ".join(required_args)} arguments.')
            
        elif not any([i in required_args for i in kwargs]) and kwargs:
            raise ValueError(f'Required {" or ".join(required_args)} args.')
        
        send_args = {k: None for k in required_args} | kwargs

        for value, index in zip(args, range(len(args))):
            send_args[required_args[index]] = value
        
        return self.func(**send_args)


class DuplicateKeyDict:
    def __init__(self):
        self._store = {}

    def __getitem__(self, name):
        return self._store[name] if len(self._store[name]) > 1 else self._store[name][0]
    
    def __setitem__(self, name, value):
        if name not in self._store:
            self._store[name] = []
        self._store[name].append(value)

    def pop(self, value):
        return self._store.pop(value)

    def __repr__(self) -> str:
        items = []
        for name, values in self._store.items():
            for value in values:
                items.append(f'{name!r}: {value!r}')
        return "{"+(", ".join(items))+"}"


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

