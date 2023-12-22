from flask import Flask
from app.models import db
from app.routes import main_app
from app.utilities import import_data, configure_app
from config.Config import AppConfig


def create_app():
    app = Flask(__name__)

    config = AppConfig('./config/config.ini')
    config.configure_app(app, db)
    # configure_app(app)
    # db.init_app(app)
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
