import requests
from time import sleep

### WICHTIG ZU IMPLEMENTIEREN ###
# access tokens nur gültig für 1 jahr
# die bilder der prdokute irgendwo speichern (ab besten in cloud, da so schneller)


### LOW PRIORITY ZU IMPLEMENTIEREN ###
# mache rein, dass ich verschiedene varianten von einem produkt bekomme (das muss dann auch in die Database)
# könnte auch machen, dass der customer sein eigenes design auf das produkt machen kann. Dafür gucke orders api.



##schreibe die die klassen rein und übertrage dann nur was du braucht in deine DB. Das ist ja die SDK!
class Product:
    def __init__(self, id, price, description, tags):
        self.id = id
        self.price = price
        self.description = description
        self.tags = tags

class ImageHolder:
    def __init__(self, product_id: int, first_img: str, second_img: str, third_img: str, forth_img: str, fifth_img: str):
        self.product_id = product_id
        self.first_img = first_img
        self.second_img = second_img
        self.third_img = third_img
        self.forth_img = forth_img
        self.fifth_img = fifth_img


class PrintifyAPIError(Exception):
    """Base exception class for Printify API errors."""
    pass

class AuthenticationError(PrintifyAPIError):
    """Raised when there's an authentication problem."""
    pass

class RateLimitError(PrintifyAPIError):
    """Raised when the API rate limit is exceeded."""
    pass


#alles handeln mit der api sowie das parsen der response klärt diese klasse!
class PrintifyHandler:
    def __init__(self, shop_id, access_token):
        self.__shop_id = shop_id
        self.__base_url = "https://api.printify.com/v1/"
        self.__access_token = access_token


    def __make_request(self, method, endpoint, data=None, params=None, retry_count=3):
        url = f"{self.__base_url}{endpoint}"
        headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.__access_token}',
            }

        for attempt in range(retry_count):
            try:
                response = requests.request(method, url, headers=headers, json=data, params=params)
                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:
                    raise AuthenticationError("Something wrong with authentification") from e

            except requests.exceptions.RequestException as e:
                if attempt == retry_count - 1:
                    raise PrintifyAPIError(f"Request failed: {str(e)}") from e

                # Exponentielles Backoff
                sleep_time = 2 ** attempt
                print(f"Request failed. Retrying in {sleep_time} seconds...")
                sleep(sleep_time)

    def get_products_info(self) -> list[Product]:     #die funktion nutze ich, um die datenbank zu füllen.
        data = self.__make_request("GET", f"shops/{self.__shop_id}/products.json")
        prodcuts_dict = data["data"]
        products_objects = []
        for product_dict in prodcuts_dict:
            id = product_dict["id"]
            description = product_dict["description"]
            tags = product_dict["tags"]
            price = product_dict["variants"][0]["price"]
            product_to_append = self.__create_single_product(id, price, description, tags)
            products_objects.append(product_to_append)
        return products_objects

    def __create_single_product(self, id, price, description, tags) -> Product:
        product = Product(id, price, description, tags)
        return product

    #hier make order: Dafür muss die post request ja die addresse enthalten, brauche also in der frontend eine form für die adresse
    #den waren korb mache ich danach. Am besten wäre eine: zur kasse button, wo dann alles aus der cart genommen wird.
    #das ordern muss auch mit dem printify handler gehen, da ich ja von dort die order sende.






















