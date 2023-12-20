
from flask import jsonify, make_response,request
from app.models import Book,User,RentedHistory
from functools import wraps
import jwt,os,logging
import pandas as pd


def send_response(data_or_message, status_code=None):
    """
    Generate a JSON response.

    Parameters:
    - data_or_message: Either the data to be included in the response or an error message.
    - status_code: The HTTP status code (default is None).

    Returns:
    - A Flask JSON response.

    """

    response_data = {
            "status": "success",
            "status code": 200,
    }

    if isinstance(data_or_message, str) and status_code != 200:
        response_data["message"] = data_or_message
        response_data["status"] = "error"
        response_data["status code"] = status_code

    elif (isinstance(data_or_message, list) and not data_or_message) or data_or_message == None:
        response_data["data"] = "No data available!"
    elif status_code == 201:
        response_data["message"] = data_or_message
        response_data["status code"] = status_code
    else:                                 
        response_data["data"] = data_or_message

    return make_response(response_data, status_code)


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
      print("Argument not provided or are not valid")
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


def export_to_csv(data, path):

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
            user = User.query.filter_by(id = data['user_id']).first()

            # Create a dictionary with only the desired attributes
            user = {
                'id': user.id,
                'isAdmin': user.isAdmin
            }
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        # returns the current logged in users context to the routes
        return  f(user, *args, **kwargs)
  
    return decorated


def to_dict(instance):

    if hasattr(instance, '__dict__'):
        # Exclude specific attributes for user instance and SQLalchemy
        excluded_attributes = ['_sa_instance_state', 'password', 'isAdmin','rented_now']
        return {key: value for key, value in vars(instance).items() if key not in excluded_attributes}
    else:
        raise NotImplementedError("Object type not supported for conversion to dictionary.")


def config_logger():
    logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:%(message)s', filename='db.log', encoding='utf-8')
    logger = logging.getLogger('logger')
    return logger


def backup():
        
    rented_books = RentedHistory.query.filter(
                   RentedHistory.end_date.is_(None),
                    ).all()
    
    print(rented_books)

    if not rented_books:
        return False
      

    data = []
    for rental in rented_books:
        data.append(to_dict(rental))

    print(data)

    df = pd.DataFrame.from_records(data, exclude=['end_date','total_cost','id'])

    df.to_csv('./output/backup.csv', index=False)

    print(f'Data has been written!')
    return True
