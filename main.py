
import os
from flask import Flask
from dotenv import load_dotenv
from app.models import db
from app.general import import_data
from app.routes import main_app


app = Flask(__name__)

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('CONNECTION_DB_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register blueprints
app.register_blueprint(main_app)


# Create the database tables
with app.app_context():
    try:
        db.create_all()
        import_data(db)
    except:
        print('DB already exists!')
  

if __name__ == '__main__':
    app.run(debug=True)


