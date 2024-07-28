import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from models.models import Base
from dotenv import load_dotenv
from flask_wtf import CSRFProtect
import uuid
from models.operations.cart_operations import get_cart_info, add_to_cart as add_to_cart_operation, calc_price_list
from models.operations.product_operations import get_products_info

# noch die login logik rein machen.
# führe noch unt tests ein.
# mache noch, dass produkte automatisch in die db eingetragen werden.
# in der database benenne id zu product_id (und bei anderen tables auch)


# bilde dich in frontend. gucke welche tools du safe brauchst.
# wiederhole den js teil. Und gucke wie man modern arbeiten (scss, typescript, frontendframeworks)
# auch gucke wie man ran geht. Wahrscheinlich nicht mit pycharm, sondern mit prepros.


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:pin11221122@localhost/paypal_flasktut" #das in database_handnler.py
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
    # hier session weg, damit ich immer neu testen kann
    session.clear()

    db = next(get_db())
    # das ist nun eine liste von dicts. Effektiv wie eine class (denk was class eig ist)!!
    products_dict = get_products_info(db) #das ist effektiv eine json mit einem key "products"

    return render_template("index.html", products_dict=products_dict)


@app.route("/add_to_cart", methods=["POST"])  # das noch prüfen. Muss frontend anpassen
def add_to_cart():  # mache, dass man hier nicht über eine url rein kommt! Das ist nur für eine post request.
    db = next(get_db())
    data = request.json

    product_id = int(data.get("item_id"))
    quantity = int(data.get("quantity", 1))

    if "cart_id" in session:
        cart_id = session.get("cart_id")
    else:
        cart_id = str(uuid.uuid4())
        session["cart_id"] = cart_id

    add_to_cart_operation(db, cart_id, product_id, quantity)
    cart_data = get_cart_info(db, cart_id)

    return jsonify({"message": "Product added to cart", "cart": cart_data})


@app.route("/cart")
def cart():
    db = next(get_db())
    cart_id = session.get("cart_id")

    # DAS HIER NUR UM KURZ ZU TESTEN. DANACH MACHE DAS WEG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    cart_id = "fcc56d58-aa90-41d1-95cf-a84753c5faef"
    ######################################################

    card_data = get_cart_info(db, cart_id)
    products = card_data.get("cart_contents", [])

    return render_template("cart.html", products=products)


@app.route("/checkout")
def checkout():
    # hiernach kommt die bestellung aufgeben!
    # nun muss ich das frontend machen!

    return render_template("checkout_page.html")  # hier muss die seite gezeigt werden, wo man addresse eingibbt


@app.route("/pay")  # hier komme nur hin, wenn ich checkout mache. Hier muss auch noch bezahl methode etc drinne sein.
def pay():
    db = next(get_db())
    cart_id = session.get("cart_id")
    cart_data = get_cart_info(db, cart_id)
    price_list = calc_price_list(cart_data)

    link = paypal_handler.make_order(price_list)
    return redirect(link)


@app.route("/shop")
def shop():
    db = next(get_db())
    products_dict = get_products_info(db)    #das ist effektiv eine json
    return render_template("shop.html", products_dict=products_dict)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/blog")
def blog():
    return render_template("blog.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/capture")
def capture():
    # die order id steht hier drin. Die aus der request zu suchen ist arsch, weil paypal keine application/json verwendet.
    order_id = request.args.get("token")
    data = paypal_handler.capture_payment(order_id)
    # hier speichere die daten in db
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)        #normalerweise muss ich damit runnen. Doch zum testen mache ich mit live server,
