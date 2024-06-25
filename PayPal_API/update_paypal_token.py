import requests
from dotenv import load_dotenv
import os

load_dotenv()
CLIENT_ID = os.environ.get("CLIENT_ID")
APP_SECRET = os.environ.get("APP_SECRET")
#ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

def replace_environ_var(file_path, var_to_replace, new_val):
    with open(file_path, "r+") as file:
        data = file.readlines()
        for i in range(len(data)):
            if var_to_replace in data[i]:
                elem = '%s="%s"\n' % (var_to_replace, new_val)
                data[i] = elem
                break
        file.seek(0)
        file.writelines(data)
        file.truncate()

def update_token(path_to_env = ".env"):
    URL_base = "https://api-m.sandbox.paypal.com"

    get_token = "/v1/oauth2/token"
    data = {'grant_type': 'client_credentials'}
    r = requests.post(URL_base + get_token, data=data, auth=(CLIENT_ID, APP_SECRET))
    r.raise_for_status()
    access_token = r.json()["access_token"]
    access_token = os.environ["ACCESS_TOKEN"] = access_token
    replace_environ_var(path_to_env, "ACCESS_TOKEN", access_token)
    return access_token