import json

def get_data():
    with open("config.json", "rb") as file:
        data = json.load(file)
    return data


def get_user_token():
    return get_data()['user_token']

def get_web():
    return get_data()['web']

def get_relay():
    return get_data()['relay']