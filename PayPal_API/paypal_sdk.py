
import uuid
import requests
from flask import current_app
from time import sleep
from datetime import datetime, timedelta



#achte, dass hier auch nur eine klasse mit einer klass method gemacht wurde.
#Mache dir gedanken, warum das so gut ist.
class ObjectToDictConverter:
    @classmethod
    def convert(cls, obj):
        """mit '{key: cls.convert(value) for key, value in obj.__dict__.items() if not key.startswith("_") and not callable(value)}'
          könnte ich zusätzlich bestimmte attribute und methods ignoriere (wobei obj.__dict__ eh keine methods enthält! Aber es gibt
          halt das 'callable' welches so verwendet werden kann"""
        if hasattr(obj, "__dict__"):
            return {key: cls.convert(value) for key, value in obj.__dict__.items()}
        elif isinstance(obj, (list, tuple)):
            return [cls.convert(item) for item in obj]
        return obj



class Amount:
    def __init__(self, value: str, currency_code: str = "EUR"):
        self.currency_code = currency_code
        self.value = value


class PurchaseUnit:
    def __init__(self, amount: Amount, reference_id: str = None):
        self.amount = amount
        self.reference_id = reference_id


class ExperienceContext:
    def __init__(self, brand_name: str = "Ayberk INC", landing_page: str = "LOGIN",
                 payment_method_preference: str = "IMMEDIATE_PAYMENT_REQUIRED",
                 payment_method_selected: str = "PAYPAL", user_action: str = "PAY_NOW",
                 return_url: str = 'http://127.0.0.1:5000/capture', cancel_url: str = 'http://127.0.0.1:5000/'):    #url_for("index") bei return_url und cancel_url
        self.brand_name = brand_name
        self.landing_page = landing_page
        self.payment_method_preference = payment_method_preference
        self.payment_method_selected = payment_method_selected
        self.user_action = user_action
        self.return_url = return_url
        self.cancel_url = cancel_url


class PaypalWallet:
    def __init__(self, experience_context: ExperienceContext):
        self.experience_context = experience_context


class PaymentSource:
    def __init__(self, paypal: PaypalWallet):
        self.paypal = paypal


class Order:
    def __init__(self, intent: str, purchase_units: list[PurchaseUnit], payment_source: PaymentSource = None, application_context=None):
        self.intent = intent
        self.purchase_units = purchase_units
        self.payment_source = payment_source
        self.application_context = application_context


class PayPalAPIError(Exception):
    """Base exception class for Printify API errors."""
    pass


# mache das token handling und das mit den request funktion!!
class PayPalAPiHanlder:
    def __init__(self, client_id, app_secret):
        self.__client_id = client_id
        self.__app_secret = app_secret
        self.__base_url = "https://api-m.sandbox.paypal.com"
        self.__access_token = None
        self.__token_expiry = None
        # self.__token_file = token_file        #wenn ich alternative speichermethode für den token haben will, implementiere so
        # self.__load_token()


    #falls ich token in einer file speichern will implementiere damit
    # def __load_token(self):
    #     if os.path.exists(self.__token_file):
    #         with open(self.__token_file, "r") as file:
    #             data = json.load(file)
    #             self.__access_token = data["access_token"]
    #             self.__token_expiry = datetime.fromisoformat(data["expiry"])

    def __get_new_token(self):   #hier eine art von error handling noch machen.
        get_token_endpoint = "/v1/oauth2/token"
        data = {'grant_type': 'client_credentials'}

        r = requests.post(self.__base_url + get_token_endpoint, data=data,
                          auth=(self.__client_id, self.__app_secret))
        r.raise_for_status()
        token_data = r.json()
        self.__access_token = token_data["access_token"]
        self.__token_expiry = datetime.now() + timedelta(seconds=token_data['expires_in'] - 300)

        #falls ich token in einer file speichern möchte, implementiere damit
        # with open(self.__token_file, "w") as file:
        #     token_data = {"access_token": self.__access_token, "expiry": self.__token_expiry.isoformat()}
        #     json.dump(token_data, file, indent=4)

    def __ensure_valid_token(self):
        if self.__access_token is None or datetime.now() >= self.__token_expiry:
            self.__get_new_token()


    def __create_Amount(self, value: str, currency_code: str = "EUR"):
        return Amount(value, currency_code)

    def __create_PurchaseUnit(self, amount: Amount, reference_id: str = None):
        return PurchaseUnit(amount, reference_id)

    def __create_ExperienceContext(self, return_url: str, cancel_url: str):
        return ExperienceContext(return_url=return_url, cancel_url=cancel_url)

    def __create_PaypalWallet(self, experience_context: ExperienceContext):
        return PaypalWallet(experience_context)

    def __create_PaymentSource(self, paypal_wallet: PaypalWallet):
        return PaymentSource(paypal_wallet)

    def __create_Order(self, intent, purchase_units: list[PurchaseUnit], payment_source: PaymentSource):
        return Order(intent, purchase_units=purchase_units, payment_source=payment_source)

    def __create_dict_for_order(self, prices):
        """erstellt die dict, der als body für die post request gesendet wird"""
        return_url = current_app.url_for('capture', _external=True)   #hier noch die links anpassen
        cancel_url = current_app.url_for('index', _external=True)   #hier noch die links anpassen

        purchase_units = [self.__create_PurchaseUnit(self.__create_Amount(str(elem)), reference_id=str(uuid.uuid4())) for elem in prices]
        experience_context = self.__create_ExperienceContext(return_url=return_url, cancel_url=cancel_url)
        paypal_wallet = self.__create_PaypalWallet(experience_context)
        payment_source = self.__create_PaymentSource(paypal_wallet)
        order = self.__create_Order(intent="CAPTURE", purchase_units=purchase_units, payment_source=payment_source)

        dict_data = ObjectToDictConverter.convert(order)

        return dict_data


    def __make_request(self, method, endpoint, data=None, params=None, retry_count=3):
        self.__ensure_valid_token()
        url = f"{self.__base_url}{endpoint}"
        headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.__access_token}',
                'PayPal-Request-Id': f'{str(uuid.uuid4())}',
            }

        for attempt in range(retry_count):
            try:
                response = requests.request(method, url, headers=headers, json=data, params=params)

                if response.status_code == 401:  # Unauthorized, möglicherweise abgelaufener Token
                    self.__get_new_token()
                    headers["Authorization"] = f"Bearer {self.__access_token}"
                    continue  # Versuche die Anfrage erneut mit dem neuen Token

                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == retry_count - 1:
                    raise PayPalAPIError(f"Request failed: {str(e)}") from e

                # Exponentielles Backoff
                sleep_time = 2 ** attempt
                print(f"Request failed. Retrying in {sleep_time} seconds...")
                sleep(sleep_time)


    def make_order(self, prices):
        """
        Does the post-request
        :param prices: tuple with prices of the items, as float with this
        :return:
        """

        dict_data = self.__create_dict_for_order(prices)                    #mit "__" vorne, kann man diese methods nur innerhalb einer klasse nutzen.
        data = self.__make_request("POST", endpoint="/v2/checkout/orders", data=dict_data)
        link = data["links"][-1]["href"]

        return link



    def capture_payment(self, order_id):
        endpoint = f"/v2/checkout/orders/{order_id}/capture"
        data = self.__make_request("POST", endpoint=endpoint)
        #hier könnte nur die daten zurück geben, die relevant sind.
        #oder könnte mehrere klassen definieren und oop mäßig diese daten in klassen machen.

        return data
