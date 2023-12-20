
import os
from flask import Flask
from dotenv import load_dotenv
from app.models import db
from app.utilities import import_data
from app.routes import main_app

def create_app():
    app = Flask(__name__)

    load_dotenv()

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('CONNECTION_DB_STRING')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_app)

    # Create the database tables
    with app.app_context():
        try:
            db.create_all()
            import_data(db)
        except:
            print('Loading Database and Tables...')

    return app

if __name__ == '__main__':
    create_app().run(debug=True)


