
from app import app,db

from app.general import export_to_csv

# Create the database tables
# try:
#     with app.app_context():
#         db.create_all()
# except Exception as e:
#     print(f"An error occurred: {e}")

if __name__ == '__main__':

    app.run(debug=True)
