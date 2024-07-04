import os
from dotenv import load_dotenv
import requests
from time import sleep
import logging
# access tokens nur gültig für 1 jahr


##schreibe die die klassen rein und übertrage dann nur was du braucht in deine DB. Das ist ja die SDK!

class Produkt:
    def __init__(self, id, price, description, tags):
        self.id = id
        self.price = price
        self.description = description
        self.tags = tags


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
    def __init__(self, shop_id):
        self.__shop_id = shop_id
        load_dotenv()
        self.__token = os.environ.get("PRINTIFY_TOKEN")
        self.__base_url = "https://api.printify.com/v1/"
        self.__headers = {"Authorization": f"Bearer {self.__token}"}

        self.__logger = logging.getLogger(__name__)     #was genau ist das hier?

    def __make_request(self, method, endpoint, data=None, params=None, retry_count=3):
        url = f"{self.__base_url}{endpoint}"

        for attempt in range(retry_count):
            try:
                response = requests.request(method, url, headers=self.__headers, json=data, params=params)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                data = response.json()
                return data

            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:
                    #falls der token abläuft, muss ich hier einen neuen generieren.
                    raise AuthenticationError("Invalid API key") from e
                elif response.status_code == 429:
                    if attempt < retry_count - 1:  # don't sleep on the last attempt
                        sleep_time = 2 ** attempt  # exponential backoff
                        self.__logger.warning(f"Rate limit hit. Retrying in {sleep_time} seconds.")
                        sleep(sleep_time)
                    else:
                        raise RateLimitError("API rate limit exceeded") from e
                else:
                    raise PrintifyAPIError(f"HTTP error occurred: {e}") from e

            except requests.exceptions.RequestException as e:
                if attempt < retry_count - 1:
                    sleep_time = 2 ** attempt
                    self.__logger.warning(f"Network error occurred. Retrying in {sleep_time} seconds.")
                    sleep(sleep_time)
                else:
                    raise PrintifyAPIError(f"Network error occurred: {e}") from e

    def __get_prodcuts_info(self):
        full_url = self.__base_url + "shops.json"
        #hier weiter machen.






















