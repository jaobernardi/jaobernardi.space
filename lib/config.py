import json

def get_data():
    with open("config.json", "rb") as file:
        data = json.load(file)
    return data


def __getattr__(name: str):
    if name.startswith("get_"):
        item = name.removeprefix("get_")
        data = get_data()
        return lambda: data[item] if item in data else None

def __dir__():
    return [f"get_{i}" for i in get_data().keys()]