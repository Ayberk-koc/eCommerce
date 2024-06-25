import json
from flask import url_for
import uuid
from update_paypal_token import update_token
from dotenv import load_dotenv
import os
import requests
from flask import url_for, current_app




base_url = "https://api-m.sandbox.paypal.com"

load_dotenv()
CLIENT_ID = os.environ.get("CLIENT_ID")
APP_SECRET = os.environ.get("APP_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")


class Amount:
    def __init__(self, value: str, currency_code: str = "EUR"):
        self.currency_code = currency_code
        self.value = value

    def to_dict(self):
        return self.__dict__


class PurchaseUnit:
    def __init__(self, amount: Amount, reference_id: str = None):
        self.amount = amount
        self.reference_id = reference_id

    def to_dict(self):
        purchaseunit_dict = self.__dict__
        if isinstance(self.amount, Amount):
            purchaseunit_dict["amount"] = self.amount.to_dict()
        return purchaseunit_dict



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

    def to_dict(self):
        return self.__dict__


class PaypalWallet:
    def __init__(self, experience_context: ExperienceContext):
        self.experience_context = experience_context

    def to_dict(self):
        paypal_wallet_dict = self.__dict__
        if isinstance(self.experience_context, ExperienceContext):
            paypal_wallet_dict["experience_context"] = self.experience_context.to_dict()
        return paypal_wallet_dict


class PaymentSource:
    def __init__(self, paypal: PaypalWallet):
        self.paypal = paypal

    def to_dict(self):
        payment_source_dict = self.__dict__
        if isinstance(self.paypal, PaypalWallet):
            payment_source_dict["paypal"] = self.paypal.to_dict()
        return payment_source_dict


class Order:
    def __init__(self, intent: str, purchase_units: list[PurchaseUnit], payment_source: PaymentSource = None, application_context=None):
        self.intent = intent
        self.purchase_units = purchase_units
        self.payment_source = payment_source
        self.application_context = application_context

    def to_dict(self):
        order_dict = self.__dict__
        if all(isinstance(elem, PurchaseUnit) for elem in self.purchase_units):     #mit all kann ich prüfen, ob alle ein bool sind
            order_dict["purchase_units"] = [elem.to_dict() for elem in self.purchase_units]
        if isinstance(self.payment_source, PaymentSource):
            order_dict["payment_source"] = self.payment_source.to_dict()
        return order_dict


def make_request(access_token, json_data):
    request_id = str(uuid.uuid4())
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'PayPal-Request-Id': f'{request_id}',
    }
    response = requests.post(base_url + '/v2/checkout/orders', headers=headers, json=json_data)
    response.raise_for_status()
    data = response.json()
    return data

def make_orders_vorlaufig(prices):
    """
    Does the post-request
    :param prices: tuple with prices of the items, as float with this
    :return:
    """

    # mache hier auch den token update, falls es nicht klappt. Das kannst du über einen try machen.
    #update_token()

    return_url = current_app.url_for('capture', _external=True)
    cancel_url = current_app.url_for('index', _external=True)

    purchase_units = [PurchaseUnit(Amount(str(elem)), reference_id=str(uuid.uuid4())) for elem in prices]       #reference_id nötig, wenn ich mehrere items habe
    experience_context = ExperienceContext(return_url=return_url, cancel_url=cancel_url)
    paypal_wallet = PaypalWallet(experience_context)
    payment_source = PaymentSource(paypal_wallet)
    order = Order(intent="CAPTURE", purchase_units=purchase_units, payment_source=payment_source)

    # with open("test_api_obj.json", "w") as file:
    #     data = order.to_dict()
    #     json.dump(data, file, indent=4)

    json_data = order.to_dict()

    try:
        data = make_request(ACCESS_TOKEN, json_data)
    except requests.HTTPError as e:
        data = make_request(update_token(), json_data)

    link = data["links"][-1]["href"]

    # with open("order_test_2.json", "w") as file:
    #     json.dump(data, file, indent=4)

    return link



