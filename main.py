import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from models.models import Base
from dotenv import load_dotenv
from flask_wtf import CSRFProtect
import uuid
from models.operations.cart_operations import get_cart_info, add_to_cart
from models.operations.product_operations import get_products_info

#noch die login logik rein machen.
#führe noch unt tests ein.
#mache noch, dass produkte automatisch in die db eingetragen werden.

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:pin11221122@localhost/paypal_flasktut"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "password für die session"

csrf = CSRFProtect(app)

from database.database_handler import get_db, engine
Base.metadata.create_all(engine)

from PayPal_API.paypal_sdk import PayPalAPiHanlder
load_dotenv("./PayPal_API/paypal_credentials.env")
PAYPAL_CLIENT_ID = os.environ.get("CLIENT_ID")
PAYPAL_APP_SECRET = os.environ.get("APP_SECRET")
paypal_handler = PayPalAPiHanlder(PAYPAL_CLIENT_ID, PAYPAL_APP_SECRET)


@app.route("/")
def index():
    db = next(get_db())
    products = get_products_info(db)    #das ist nun eine liste von dicts. Effektiv wie eine class (denk was class eig ist)!!

    return render_template("index.html", products=products)

@app.route("/add_to_cart", methods=["POST"])        #das noch prüfen. Muss frontend anpassen
def add_to_cart():              #mache, dass man hier nicht über eine url rein kommt! Das ist nur für eine post request.
    db = next(get_db())
    data = request.json
    product_id = int(data.get("id"))
    quantity = int(data.get("quantity", 1))

    if "cart_id" in session:
        cart_id = session["cart_id"]
    else:
        cart_id = str(uuid.uuid4())
        session["cart_id"] = cart_id

    add_to_cart(db, cart_id, product_id, quantity)
    cart_data = get_cart_info(db, cart_id)

    return jsonify({"message": "Product added to cart", "cart": cart_data})


@app.route("/checkout")
def checkout():
    #hier muss ich die produkte in einer card nehmen und ins checkout bringen.
    products = ""
    return render_template("cart_checkout.html", products=products)    # hier muss die seite gezeigt werden, wo man addresse eingibbt

@app.route("/pay")
def pay():
    link = paypal_handler.make_order([10, 20])  #hier die preise der items.
    #muss noch daten in db speichern
    return redirect(link)

@app.route("/capture")
def capture():
    order_id = request.args.get("token")    #die order id steht hier drin. Die aus der request zu suchen ist arsch, weil paypal keine application/json verwendet.
    data = paypal_handler.capture_payment(order_id)
    #hier speichere die daten in db
    return redirect(url_for("index"))





if __name__ == "__main__":
    app.run(debug=True)