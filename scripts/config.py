import json


class Node(object):
    def __init__(self, d):
        self._dict = {}
        self._original_dict = d
        self.fetch()

    def fetch(self):
        for key in self._original_dict:
            if isinstance(self._original_dict[key], dict):
                self._dict[key] = Node(self._original_dict[key])
            else:
                self._dict[key] = self._original_dict[key]

    def __getattr__(self, attr):
        return self._dict[attr]

    def __setattr__(self, name, value):
        __dict__ = super().__dir__()
        if '_original_dict' in __dict__:
            if name in super().__getattribute__('_original_dict'):
                self._original_dict[name] = value
                self.fetch()
        else:
            super().__setattr__(name, value)

    def __repr__(self):
        return self._original_dict.__repr__()


class Config(Node):
    def __init__(self):
        config = open("config.json", "rb")
        super().__init__(json.load(config))
