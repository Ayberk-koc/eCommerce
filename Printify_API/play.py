import os
from dotenv import load_dotenv
import requests

# access tokens nur gültig für 1 jahr
base_url = "https://api.printify.com/v1/"

shop_id = 16664796


load_dotenv()
Printify_Token = os.environ.get('PRINTIFY_TOKEN')

header = {"Authorization": f"Bearer {Printify_Token}"}

class PrintifyHandler:
    def __init__(self):
        load_dotenv()
        self.token = os.environ.get("PRINTIFY_TOKEN")


# response = requests.get(base_url + "shops.json", headers=header)
# response.raise_for_status()
# data = response.json()

response = requests.get(base_url + f"shops/{shop_id}/products/66853fb5e4bee08b6d00ac90.json", headers=header)
response.raise_for_status()
data = response.json()



import json
with open("test2_api.json", "w") as file:
    json.dump(data, file, indent=4)





