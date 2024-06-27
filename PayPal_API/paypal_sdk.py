import uuid
from dotenv import load_dotenv
import os
import requests
from flask import current_app

base_url = "https://api-m.sandbox.paypal.com"


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

class PayPalAPiHanlder:
    def __init__(self):
        load_dotenv()
        self.__client_id = os.environ.get("CLIENT_ID")  #das "__" damit diese attribute (oder method) private sind, also nur innerhalb der class verwendet werden können
        self.__app_secret = os.environ.get("APP_SECRET")
        self.__access_token = os.environ.get("ACCESS_TOKEN")

    def __update_token(self, path_to_env=".env"):
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

        get_token_endpoint = "/v1/oauth2/token"

        data = {'grant_type': 'client_credentials'}
        r = requests.post(base_url + get_token_endpoint, data=data, auth=(self.__client_id, self.__app_secret))
        r.raise_for_status()
        self.__access_token = r.json()["access_token"]
        replace_environ_var(path_to_env, "ACCESS_TOKEN", self.__access_token)

        return self.__access_token

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

    def __make_post_request(self, url_next_to_base: str, dict_data=None):      #muss irgendwie so machen, dass man diese method nur innerhalb dieser klasse nutzen kann. Damit die nutzung außerhalb der class einfacher ist!
        def inner(access_token, url_next_to_base, dict_data):
            """macht die request. Muss mit try except block arbeiten, weil ich mögl den access token updaten muss
            das "url_next_to_base" ist der endpoint (halt bis auf die base url, also zb: '/v2/checkout/orders')
            """
            request_id = str(uuid.uuid4())
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'PayPal-Request-Id': f'{request_id}',
            }
            response = requests.post(base_url + url_next_to_base, headers=headers, json=dict_data)
            response.raise_for_status()
            data = response.json()
            return data
        try:
            data = inner(self.__access_token, url_next_to_base, dict_data)
        except requests.HTTPError as e:
            data = inner(self.__update_token(), url_next_to_base, dict_data)
        return data

    def make_order(self, prices):
        """
        Does the post-request
        :param prices: tuple with prices of the items, as float with this
        :return:
        """

        dict_data = self.__create_dict_for_order(prices)                    #mit "__" vorne, kann man diese methods nur innerhalb einer klasse nutzen.
        data = self.__make_post_request('/v2/checkout/orders', dict_data)
        link = data["links"][-1]["href"]

        return link

    def capture_payment(self, order_id):
        url_beyond_base = f"/v2/checkout/orders/{order_id}/capture"
        data = self.__make_post_request(url_next_to_base=url_beyond_base)
        #hier könnte nur die daten zurück geben, die relevant sind.
        #oder könnte mehrere klassen definieren und oop mäßig diese daten in klassen machen.

        return data
