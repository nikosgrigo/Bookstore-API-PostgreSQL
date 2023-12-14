
from flask import Response
import json
import pandas as pd
from app.models import Book

def send_response(response_data,status:str,status_code:int):

   '''
   Send an HTTP response with JSON content.

   Parameters:
   - response_data (dict): The data to be included in the response.
   - status (str): The status of the response, either 'success' or another status.
   - status_code (int): The HTTP status code to be included in the response.

   Returns:
   - Response: An HTTP response with JSON content.

   '''

   if status == 'success' and not type(response_data) == str:
      return Response(json.dumps({"data":response_data,
                                  "status":status,
                                  "status code":status_code}),
                                 content_type='application/json', status=status_code)
   
   return Response(json.dumps({"message":response_data,
                               "status":status,
                               "status code":status_code}),
                                 content_type='application/json', status=status_code)


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
      return False
   return True


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


def days_between(d1, d2):

   '''
   Calculate the number of days between two dates.

   Parameters:
   - d1 (str): The first date in the format 'YYYY-MM-DD'.
   - d2 (str): The second date in the format 'YYYY-MM-DD'.

   Returns:
   - int: The number of days between the two dates.

   '''

   dt0 = pd.to_datetime(d1, format = '%Y-%m-%d')
   dt1 = pd.to_datetime(d2, format = '%Y-%m-%d')
   return (dt1 - dt0).days


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

