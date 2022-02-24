import os


def load_handlers():
    for handler in os.listdir("handlers"):
        if handler.endswith(".py"):
            __import__("handlers."+handler.removesuffix(".py"))