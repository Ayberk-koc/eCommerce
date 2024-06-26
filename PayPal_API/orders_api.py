import uuid
from dotenv import load_dotenv
import os
import requests
from flask import current_app


#könnte eine allgemeine klasse machen, die alles paypal sachen handelt! Da müsste ich alles in eine klasse schließen
#auch das token handling, das Kreieren eines links bei orders und das captures etc. Da Sollte am besten mit abstrakten klassen
#machen (weil ich immer die "to_dict" methode nutze). Auch mache irgendwie das serialisieren für die json response!

base_url = "https://api-m.sandbox.paypal.com"


class PayPalTokenHandler:
    def __init__(self):
        load_dotenv()
        self.client_id = os.environ.get("CLIENT_ID")
        self.app_secret = os.environ.get("APP_SECRET")
        self.access_token = os.environ.get("ACCESS_TOKEN")

    def update_token(self, path_to_env=".env"):
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
        r = requests.post(base_url + get_token_endpoint, data=data, auth=(self.client_id, self.app_secret))
        r.raise_for_status()
        self.access_token = r.json()["access_token"]
        replace_environ_var(path_to_env, "ACCESS_TOKEN", self.access_token)

        return self.access_token


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
        if all(isinstance(elem, PurchaseUnit) for elem in self.purchase_units):     #mit all kann ich prüfen, ob alle truely sind
            order_dict["purchase_units"] = [elem.to_dict() for elem in self.purchase_units]
        if isinstance(self.payment_source, PaymentSource):
            order_dict["payment_source"] = self.payment_source.to_dict()
        return order_dict



class PayPalAPiHanlder:
    def __init__(self):
        self.__paypal_token_handler = PayPalTokenHandler()          #das "__" damit diese attribute (oder method) private sind, also nur innerhalb der class aufrufbar.

    def __make_post_request(self, url_next_to_base: str, json_data=None):      #muss irgendwie so machen, dass man diese method nur innerhalb dieser klasse nutzen kann. Damit die nutzung außerhalb der class einfacher ist!
        def inner(access_token, url_next_to_base, json_data):
            """macht die request. Muss mit try except block arbeiten, weil ich mögl den access token updaten muss
            das "url_next_to_base" ist der endpoint (halt bis auf die base url, also zb: '/v2/checkout/orders')
            """
            request_id = str(uuid.uuid4())
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'PayPal-Request-Id': f'{request_id}',
            }
            response = requests.post(base_url + url_next_to_base, headers=headers, json=json_data)
            response.raise_for_status()
            data = response.json()
            return data
        try:
            data = inner(self.__paypal_token_handler.access_token, url_next_to_base, json_data)
        except requests.HTTPError as e:
            data = inner(self.__paypal_token_handler.update_token(), url_next_to_base, json_data)
        return data


    def __create_json_for_order(self, prices):
        """erstellt den json string, der als body für die post request gesendet wird"""
        return_url = current_app.url_for('capture', _external=True)   #hier noch die links anpassen
        cancel_url = current_app.url_for('index', _external=True)   #hier noch die links anpassen

        purchase_units = [PurchaseUnit(Amount(str(elem)), reference_id=str(uuid.uuid4())) for elem in prices]       #reference_id nötig, wenn ich mehrere items habe
        experience_context = ExperienceContext(return_url=return_url, cancel_url=cancel_url)
        paypal_wallet = PaypalWallet(experience_context)
        payment_source = PaymentSource(paypal_wallet)
        order = Order(intent="CAPTURE", purchase_units=purchase_units, payment_source=payment_source)

        # with open("test_api_obj.json", "w") as file:
        #     data = order.to_dict()
        #     json.dump(data, file, indent=4)

        json_data = order.to_dict()
        return json_data


    def make_order(self, prices):
        """
        Does the post-request
        :param prices: tuple with prices of the items, as float with this
        :return:
        """

        json_data = self.__create_json_for_order(prices)                    #mit "__" vorne, kann man diese methods nur innerhalb einer klasse nutzen.
        data = self.__make_post_request('/v2/checkout/orders', json_data)
        link = data["links"][-1]["href"]

        return link

    def capture_payment(self, order_id):
        url_beyond_base = f"/v2/checkout/orders/{order_id}/capture"
        data = self.__make_post_request(url_next_to_base=url_beyond_base)

        return data



