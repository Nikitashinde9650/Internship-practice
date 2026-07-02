from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# MySQL Database Connection
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root%40123@localhost/company"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)