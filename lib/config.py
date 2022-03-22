import json

def get_data():
    with open("config.json", "rb") as file:
        data = json.load(file)
    return data

def get_stream_auth():
    return get_data()['stream_auth']

def get_user_token():
    return get_data()['user_token']

def get_web():
    return get_data()['web']
