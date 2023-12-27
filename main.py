from flask import Flask
from app.models import db
from app.routes import main_app
from app.utilities import import_data
from config.Config import AppConfig
import logging

# Configure the global logger in main.py
logging.basicConfig(
    filename='db.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
)

app = Flask(__name__)

config = AppConfig()
config.configure_app(app, db)

app.register_blueprint(main_app)


# logger = config_logger()
logging.info('Flask app stared')

# Create the database tables
with app.app_context():
    try:
        db.create_all()
        import_data(db)
    except Exception as e:
         print('Loading Database and Tables...')

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        logging.info('Flask app closed')


