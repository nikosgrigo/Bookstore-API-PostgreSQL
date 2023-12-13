
from flask import Response
import json
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
import pandas as pd
from app.models import Book

def send_response(response_data,status:str,status_code:int):
   if status == 'success' and not type(response_data) == str:
      return Response(json.dumps({"data":response_data,"status":status,"status code":status_code}), content_type='application/json', status=status_code)
   else:
      return Response(json.dumps({"message":response_data,"status":status,"status code":status_code}), content_type='application/json', status=status_code)

def is_date_args_valid(argsList):

   start_date = argsList.get('start') #(i.e. ?start=YYYY-MM-DD)
   end_date = argsList.get('end')     #(i.e. &end=YYYY-MM-DD)

   if not start_date or not end_date or start_date > end_date:     #(+check if start date is smaller than end date)
      print("Argument not provided")
      return False
   return True


def create_session():
   engine = create_engine(os.getenv('CONNECTION_DB_STRING'))
   Session = sessionmaker(bind=engine)
   session = Session()
   return session


def import_data(db):
    # Load data from CSV file
   csv_path = './data/Books.csv'
   data = pd.read_csv(csv_path,nrows=1000)

    # Iterate over rows and add data to the database
   for index, row in data.iterrows():
        book = Book(
            isbn=row['ISBN'],
            title=row['Book-Title'],
            author=row['Book-Author'],
            year_of_publication=row['Year-Of-Publication'],
            publisher=row['Publisher'],
            avgrating=0,
            isAvailable=True,
            image_url_s=row['Image-URL-S'],
            image_url_m=row['Image-URL-M'],
            image_url_l=row['Image-URL-L']
        )
        db.session.add(book)

      # Commit changes to the database
   db.session.commit()


def days_between(d1, d2):
   dt0 = pd.to_datetime(d1, format = '%Y-%m-%d')
   dt1 = pd.to_datetime(d2, format = '%Y-%m-%d')
   return (dt1 - dt0).days

def user_data_is_valid(data):
   return True