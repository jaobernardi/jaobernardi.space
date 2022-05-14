from string import ascii_letters
from random import choices
from hashlib import sha512, sha256

import os
import inspect


def load_handlers():
    for handler in os.listdir("handlers"):
        if handler.endswith(".py"):
            __import__("handlers."+handler.removesuffix(".py"))


# Function wrapper to require at least one argument
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


def random_string(length=16):
    charset = ascii_letters + "".join([str(i) for i in range(10)])
    return "".join(choices(charset, k=length))


def hash(string, salt=''):
    _hash = sha256()
    _hash.update(string.encode('utf-8'))
    _hash.update(salt.encode('utf-8'))
    _hash = _hash.hexdigest()
    return _hash