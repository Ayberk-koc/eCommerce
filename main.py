from dotenv import load_dotenv
from flask import Flask, g
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


@app.route("/")
def index():                              #um order zu setzten brauche ich eine token. Manchmal muss man die updaten
    g.session = Session()
    return "halslo"





if __name__ == "__main__":
    app.run(debug=True)