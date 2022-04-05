import json

def get_data():
    with open("config.json", "rb") as file:
        data = json.load(file)
    return data

def get_otp():
    return get_data()['otp']

def get_database():
    return get_data()['database']

def get_private_key():
    return get_data()['private_key']

def get_public_key():
    return get_data()['public_key']

def get_https_redirect():
    return get_data()['https_redirect']

def get_spotify_client_id():
    return get_data()['spotify_client_id']

def get_https_redirect_settings():
    return get_data()['https_redirect_settings']

def get_stream_auth():
    return get_data()['stream_auth']

def get_user_token():
    return get_data()['user_token']

def get_web():
    return get_data()['web']

def get_root():
    return get_data()['web_root']

def get_rate():
    return get_data()['connection_rate']