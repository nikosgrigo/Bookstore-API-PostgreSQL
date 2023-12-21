
from flask import jsonify, make_response,request
from app.models import Book,User,RentedHistory
from functools import wraps
import jwt,os,logging
import pandas as pd
from datetime import datetime


def send_response(response_content, status_code=None):
    """
    Generate a JSON response.

    Parameters:
    - response_content: Either the data to be included in the response or an error message.
    - status_code: The HTTP status code (default is None).

    Returns:
    - A Flask JSON response.
    """

    response_data = {"status": "success", "status code": 200}

    if status_code and status_code != 200 and status_code != 201:
        response_data.update({"status": "error", "message": response_content, "status code": status_code})
    
    elif response_content is None:
        response_data["data"] = "No data available!"
    
    elif status_code == 201:
        response_data.update({"message": response_content,"status": "success", "status code": status_code})
    
    elif isinstance(response_content, (float, int)):
        response_data["total revenue"] = response_content
    
    else:
        response_data["data"] = response_content

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


def export_to_csv(data, filename: str):

    """
    Export data for rental and total revenue to CSV files.

    Parameters:
        - data (list or int): The data to be exported.
        - filename (str): The filename for the CSV file.
    """

    #Create new timestamp
    date = datetime.now()      
    date = date.strftime('%Y-%m-%d')

    #Create path 
    path = f"./output/{filename}-{date}.csv"

    # Format data before passsing them on Dataframe constructor 
    df = pd.DataFrame(data) if filename.lower() == 'rentals' else pd.DataFrame({"total_revenue": [data]})

    # Check if the file exists - if not create backup
    if not os.path.exists(path):
        df.to_csv(path, index=False)
        print(f"New CSV file '{filename}-{date}.csv' created with data.")
    else:
        print(f"Backup already exists for '{filename}-{date}.csv'. No action taken.")


def user_data_is_valid(data:dict):
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
    raise NotImplementedError("Object type not supported for conversion to dictionary.")


def config_logger():
    logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:%(message)s',
                        filename='db.log',
                        encoding='utf-8')
    logger = logging.getLogger('logger')
    return logger


def backup():
        
    rented_books = RentedHistory.query.filter(
                   RentedHistory.end_date.is_(None),
                    ).all()
    
    if not rented_books:
        return False
      
    data = []
    for rental in rented_books:
        data.append(to_dict(rental))

    #Create new timestamp
    date = datetime.now()      
    date = date.strftime('%Y-%m-%d')

    #Create path 
    path = f"./output/Backup-{date}.csv"

    # Check if the file exists - if not create backup
    if not os.path.exists(path):
        df = pd.DataFrame.from_records(data, exclude=['end_date','total_cost','id'])
        df.to_csv(path, index=False)
        return True
    else:
        print(f"Backup already exists. No action taken.")
        return False



