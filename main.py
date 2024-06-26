from flask import Flask, g, render_template
from sqlalchemy import create_engine
from models import Base, InitialTable
from sqlalchemy.orm import sessionmaker
from PayPal_API.orders_api import PayPalAPiHanlder



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:pin11221122@localhost/flask_tut"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "password für die session"

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
paypal_handler = PayPalAPiHanlder()


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
    return render_template("index.html")

@app.route("/order")
def order():
    link = paypal_handler.make_order([10, 20])
    return link



if __name__ == "__main__":
    app.run(debug=True)