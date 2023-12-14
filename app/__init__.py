
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from app.models import db

app = Flask(__name__)

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('CONNECTION_DB_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

from app import routes, models

