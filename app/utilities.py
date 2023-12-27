"""
Module Documentation: utilities.py

This module provides utility functions for handling responses, validating data, and interacting with the database.

Functions:
- send_response: Generate a JSON response for HTTP requests.
- is_date_args_valid: Check if provided date URL arguments are valid.
- import_data: Import data from a CSV file into the database.
- export_to_csv: Export data to CSV files.
- user_data_is_valid: Validate incoming user registration data.
- token_required: Decorator function for routes requiring authentication.
- to_dict: Convert SQLAlchemy model instances to dictionaries.
- config_logger: Configure the logger for logging to a file.
- backup: Create a backup of current rented books to a CSV file.

"""
from datetime import datetime
from functools import wraps

import jwt
import logging
import os
import pandas as pd
from flask import jsonify, make_response, request

from config.Config import AppConfig
from app.models import Book, User, RentedHistory


def send_response(response_content, status_code=None):
    """
    Generate a JSON response.

    Parameters:
    - response_content (string or list or dict): Either the data to be included in the response or an error message.
    - status_code (int): The HTTP status code (default is None).

    Returns:
    - A Flask JSON response.
    """

    response_data = {"status": "success", "status code": 200}

    if status_code and status_code != 200 and status_code != 201:
        response_data.update({"status": "error", "message": response_content, "status code": status_code})

    elif response_content is None:
        response_data["data"] = "No data available!"

    elif status_code == 201:
        response_data.update({"message": response_content, "status": "success", "status code": status_code})

    elif isinstance(response_content, (float, int)):
        response_data["total revenue"] = response_content

    else:
        response_data["data"] = response_content

    return make_response(response_data, status_code)


def is_date_args_valid(argsList: dict):
    """
    Check if the provided date url arguments are valid.

    Parameters:
    - args_list (dict): A dictionary containing date arguments in the format 'YYYY-MM-DD'

    Returns:
    - bool: True if the date arguments are valid, False otherwise.

    """
    start_date = argsList.get('start')
    end_date = argsList.get('end')

    if not start_date or not end_date or start_date > end_date:
        print("Argument not provided or are not valid")
        return []
    return [start_date, end_date]


def import_data(db):
    """
   Import data from a CSV file into Bookstore database.

   Parameters:
   - db: The SQLAlchemy database instance.

   """
    
    # Create sample user data
    users_data = [
        {"username": "user1", "email": "user1@gmail.com", "password": "user1"},
        {"username": "user2", "email": "user2@gmail.com", "password": "user2"},
        {"username": "admin", "email": "admin@gmail.com", "password": "admin"},
        {"username": "demo", "email": "demo@gmail.com", "password": "demo"},
    ]

    # Add rented history records to the database
    rented_history_data = [
        {"total_cost": 0, "start_date": "2023-12-10","end_date": None, "isbn": "042511774X", "user_id": 4},
        {"total_cost": 0,"start_date": "2023-12-12","end_date": None, "isbn": "1853262404", "user_id": 1},
        {"total_cost": 3, "start_date": "2023-12-18", "end_date": "2023-12-21", "isbn": "043922165X", "user_id": 1},
        {"total_cost": 4.5, "start_date": "2023-12-21", "end_date": "2023-12-27", "isbn": "1841721522", "user_id": 2},
    ]

    # Add users to the database
    for rental in rented_history_data:
        new_rental = RentedHistory(rental.get('total_cost'),
                          rental.get('start_date'),
                          rental.get('end_date'),
                          rental.get('isbn'),
                          rental.get('user_id'))
        db.session.add(new_rental)

    # Add users to the database
    for user_data in users_data:
        new_user = User(user_data.get('username'),
                        user_data.get('email'),
                        user_data.get('password'))
        db.session.add(new_user)

    db.session.commit()


    data = pd.read_csv('./data/Books.csv')

    # Iterate over rows and add data to the database
    for _, row in data.iterrows():
        book = Book(
            isbn=row['ISBN'],
            title=row['Book-Title'],
            author=row['Book-Author'],
            year_of_publication=row['Year-Of-Publication'],
            publisher=row['Publisher'],
            image_url_s=row['Image-URL-S'],
            image_url_m=row['Image-URL-M'],
            image_url_l=row['Image-URL-L'],
            rented_now=row['User-ID'],
            rating=row['Book-Rating'],
            isAvailable=True
        )
        db.session.add(book)


    # Commit changes to the database
    db.session.commit()

    logging.info('Database and Tables data imported successfully')


def export_to_csv(data, filename: str):
    """
    Export data for rental and total revenue to CSV files.

    Parameters:
        - data (list or int): The data to be exported.
        - filename (str): The filename for the CSV file.
    """
    try:
        # Create new timestamp
        date = datetime.now()
        date = date.strftime('%Y-%m-%d')

        # Create path
        path = f"output/{filename}-{date}.csv"

        # Format data before passing them on Dataframe constructor
        df = pd.DataFrame(data) if filename.lower() == 'rentals' else pd.DataFrame({"total_revenue": [data]})

        # Check if the file exists - if not create backup
        if not os.path.exists(path):
            df.to_csv(path, index=False)
            logging.info(f"New CSV file '{filename}-{date}.csv' created with data.")
        else:
            logging.warning(f"Backup already exists for '{filename}-{date}.csv'. No action taken.")
    except Exception as e:
        logging.error(e)


def user_data_is_valid(data: dict):
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
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            config = AppConfig()
            data = jwt.decode(token, config.get_secret_key(), algorithms=['HS256'])
            user = User.query.filter_by(id=data['user_id']).first()

            # Create a dictionary with only the desired attributes
            user = {
                'id': user.id,
                'isAdmin': user.isAdmin
            }

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}),
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(user, *args, **kwargs)

    return decorated


def to_dict(instance):
    if hasattr(instance, '__dict__'):
        # Exclude specific attributes for user instance and SQLalchemy
        excluded_attributes = ['_sa_instance_state', 'password', 'isAdmin', 'rented_now']
        return {key: value for key, value in vars(instance).items() if key not in excluded_attributes}
    logging.warning("Object type not supported for conversion to dictionary.")


def backup():
    rented_books = RentedHistory.query.filter(
        RentedHistory.end_date.is_(None),
    ).all()

    if not rented_books:
        return False

    data = [to_dict(rental) for rental in rented_books]

    # Create new timestamp
    date = datetime.now()
    date = date.strftime('%Y-%m-%d')

    # Create path
    path = f"output/Backup-{date}.csv"

    # Check if the file exists - if not create backup
    if not os.path.exists(path):
        df = pd.DataFrame.from_records(data, exclude=['end_date', 'total_cost', 'id'])
        df.to_csv(path, index=False)
        logging.info('Backup created successfully')
        return True
    else:
        logging.warning("Backup already exists. No action taken.")
        return False
