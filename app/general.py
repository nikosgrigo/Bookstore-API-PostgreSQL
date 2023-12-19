
from flask import jsonify, make_response
import pandas as pd
from app.models import Book,User

from functools import wraps
import jwt,os
from flask import request

def send_response(response_data):

   '''
   Send an HTTP response with JSON content.

   Parameters:
   - response_data (dict): The data to be included in the response.
   - status (str): The status of the response, either 'success' or another status.
   - status_code (int): The HTTP status code to be included in the response.

   Returns:
   - Response: An HTTP response with JSON content.

   '''

   if response_data and not isinstance(response_data, str):
      status_code = 200
      response = jsonify({"data": response_data, "status": "success", "status code":status_code})
   else:
      status_code = 404
      response = jsonify({"message": "No data available", "status": "error", "status code":status_code})

   return make_response(response, status_code)

def is_date_args_valid(argsList):

   '''
   Check if the provided date url arguments are valid.

   Parameters:
   - args_list (dict): A dictionary containing date arguments in the format 'YYYY-MM-DD'

   Returns:
   - bool: True if the date arguments are valid, False otherwise.

   '''

   start_date = argsList.get('start') 
   end_date = argsList.get('end')     

   if not start_date or not end_date or start_date > end_date:
      print("Argument not provided")
      return []
   return [start_date,end_date]

def import_data(db):

   '''
   Import data from a CSV file into Bookstore database.

   Parameters:
   - db: The SQLAlchemy database instance.

   '''


   data = pd.read_csv('./data/Books.csv')  


    # Iterate over rows and add data to the database
   for index, row in data.iterrows():
        book = Book(
            isbn = row['ISBN'],
            title = row['Book-Title'],
            author = row['Book-Author'],
            year_of_publication = row['Year-Of-Publication'],
            publisher = row['Publisher'],
            image_url_s = row['Image-URL-S'],
            image_url_m = row['Image-URL-M'],
            image_url_l = row['Image-URL-L'],
            rented_now = row['User-ID'],
            rating = row['Book-Rating'],
            isAvailable = True
        )
        db.session.add(book)

      # Commit changes to the database
   db.session.commit()

def export_to_csv(data,path):

   """
    Export data for rental and total revenue to CSV files.

    Parameters:
        - data (DataFrame or any): The data to be exported.
        - path (str): The path or filename for the CSV file.

    Note:
        - If `path.lower() == 'rentals'`, data is assumed to be a DataFrame.
        - If `path.lower() != 'rentals'`, data is assumed to be a  value.

   """
       
   if path.lower() == 'rentals':
      df = pd.DataFrame(data) 
      df.to_csv(f"./output/{path}.csv", index=False)
   else:
      df = pd.DataFrame({"total_revenue": [data]}) 
      df.to_csv(f"./output/{path}.csv", index=False)

def user_data_is_valid(data):
   # Validate incoming data
    if 'username' not in data or 'email' not in data or 'password' not in data:
       return False
    return True

# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            current_user = User.query.filter_by(id = data['user_id']).first()
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        # returns the current logged in users context to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated