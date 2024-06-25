from dotenv import load_dotenv
from flask import Flask, g, render_template
from sqlalchemy import create_engine
from models import Base, InitialTable
from sqlalchemy.orm import sessionmaker
import os
load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:pin11221122@localhost/flask_tut"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "password für die session"

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
    return render_template("index.html")

@app.route("/order")
def order():
    #hier mache dass man eine paypal order setzt
    return



if __name__ == "__main__":
    app.run(debug=True)