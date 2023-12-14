
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from app.general import import_data
from app.models import db

app = Flask(__name__)

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('CONNECTION_DB_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

from app import routes, models


# Create the database tables - RUN this one time
# try:
#     with app.app_context():
#         db.create_all()
#         import_data(db)

        
# except Exception as e:
#     print(f"An error occurred: {e}")
