from app.models import RentedHistory

import pandas as pd
from datetime import datetime
from flask import jsonify, make_response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

class HistoryService:

    def get_rented_book(self,book_id, user_id):

        '''
        Get information about a rented book based on its rented ID.

        Parameters:
        - rented_id: The rented ID of the book.

        Returns:
        - The rented book information if found, None otherwise.

        '''
  

        data = RentedHistory.query.filter_by(isbn = book_id, user = user_id).first()
        if data: return data 
        return None

    def calculate_rental_fee(self,start,end):

        '''
        Calculate the rental fee based on the start and end dates of the rental period.

        Parameters:
        - start (str): The start date of the rental period in the format 'YYYY-MM-DD'.
        - end (str): The end date of the rental period in the same format.

        Returns:
        - float: The calculated rental fee.

        '''
  
        dt0 = pd.to_datetime(start, format = '%Y-%m-%d')
        dt1 = pd.to_datetime(end, format = '%Y-%m-%d')
        days = (dt1 - dt0).days

        if days <= 3:
            return days*1
        return 3*1 + (days-3)*0.5
    
    def return_book(self, rentedBook, db, isAdmin):

        '''
        Return a rented book, update book availability, and record the return transaction in the rented history.

        Parameters:
        - rentedBook: The rented book instance to be returned.
        - db: The SQLAlchemy database instance.

        Returns:
        - float: The calculated rental fee for the returned book.

        '''
        if not isAdmin:
            response = jsonify({"message": "Oops sorry you don't have access!", "status": "error", "status code":403})
            return make_response(response, 403)

        if not rentedBook:
            status_code = 400
            response = jsonify({"message": "Book not found or not currently rented", "status": "error", "status code":status_code})
            return make_response(response, status_code)


        try:
            # 1. Change Availability on Book table to True using foreign key
            book = rentedBook.book
            book.isAvailable = True

            # 2. Update end_date for current book

            date = datetime.now()      
            end_date = date.strftime('%Y-%m-%d')

            rentedBook.end_date = end_date

            #3. Calculate rental fee based on rented days
            rental_fee = self.calculate_rental_fee(rentedBook.start_date,end_date)


            #4. Update total_cost on the instance
            rentedBook.total_cost = rental_fee

            db.session.commit()

            response = jsonify({"message": "Book returned successfully","rental_fee":rental_fee, "status": "success", "status code":200})
            return make_response(response, 200)
        except SQLAlchemyError as e:
            
            print(f"Database error: {e}")
            response = jsonify({"message": "Error occurred during book return", "status": "error", "status code": 500})
            return make_response(response, 500)
        
    def get_all_rented_books_for_period(self, start, end, return_type):

        '''
        Get all rented books within a specified rental period.

        Parameters:
        - start (str): The start date of the rental period in the format 'YYYY-MM-DD'.
        - end (str): The end date of the rental period in the same format'.
        - return_type: The type of return information to retrieve.

        Returns:
        - list: A list of rented books within the specified rental period.

        '''

        rented_books = RentedHistory.query.filter((RentedHistory.start_date >= start) &
                                                (or_(RentedHistory.end_date <= end, 
                                                     RentedHistory.end_date.is_(None)))).all()


        if return_type.lower() == "list":
            data = []
            for instance in rented_books:
                book = instance.book
                data.append(book.to_dict())
            return data
        return rented_books
    
    def calculate_total_rental_fee(self, rented_books):

        '''
        Calculate the total rental fee for a list of rented books.

        Parameters:
        - rented_books: A list of rented books.

        Returns:
        - float: The total rental fee for the provided rented books.

        '''

        total = sum(book.total_cost for book in rented_books)
        return total
        
    