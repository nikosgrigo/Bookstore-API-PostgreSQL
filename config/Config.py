import configparser
import os


class AppConfig:

    def __init__(self, path):
        self.config = configparser.ConfigParser()
        self.config_file = path

        # Read configuration from the file
        self.read_config()

    def read_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            raise FileNotFoundError(f"Config file '{self.config_file}' not found.")

    def configure_app(self, app, db):
        # Configure SQLAlchemy
        db_url = self.config.get('DatabaseURL', 'connection_db_string').format(**self.config['Database'])
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = self.config.get('Database', 'secret_key')

        db.init_app(app)

    def get_secret_key(self):
        return self.config.get('Database', 'secret_key')
