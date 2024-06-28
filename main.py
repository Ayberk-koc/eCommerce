from flask import Flask, g, render_template, request, redirect, url_for
from models import User, Base

#sollte auch eine app configuration datei machen. Dort schreibe ich dann auch die paypal base url rein.

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:pin11221122@localhost/paypal_flasktut"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "password für die session"

from PayPal_API.paypal_sdk import PayPalAPiHanlder
paypal_handler = PayPalAPiHanlder()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


@app.before_request
def before_request():           #ist es wirklich schlau, jedes mal eine connection zu öffnen? NEIN, mache später raus
    g.session = Session()       #hier ist die connection zur datenbank! Das "g" ist ein shared object für eine request. Kann es funktionsübergreifend nutzen

@app.teardown_request
def teardown_request(exception=None):
    session = getattr(g, 'session', None)
    if session is not None:
        session.close()


@app.route("/")
def index():
    user = g.session.query(User).first()
    print(user.email)
    return render_template("index.html")

@app.route("/order")
def order():
    link = paypal_handler.make_order([10, 20])
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