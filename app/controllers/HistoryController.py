from app.models import RentedHistory
from app.utilities import to_dict,send_response
import pandas as pd
from datetime import datetime
from sqlalchemy import or_

class HistoryService:

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
    

    def return_book(self, db, book_id):

        #1. Find book on history table based on isbn and user-id
        rentedBook = RentedHistory.query.filter(
            RentedHistory.isbn == book_id,
            RentedHistory.end_date.is_(None),
        ).first()

        if not rentedBook:
            return send_response("Book not found or not currently rented", 400)
        
        #2. Change Availability on Book table to True using foreign key
        book = rentedBook.book
        book.isAvailable = True

        #3. Update end_date for current book

        date = datetime.now()      
        end_date = date.strftime('%Y-%m-%d')

        rentedBook.end_date = end_date

        #4. Calculate rental fee based on rented days
        rental_fee = self.calculate_rental_fee(rentedBook.start_date,end_date)


        #5. Update total_cost on the instance
        rentedBook.total_cost = rental_fee

        db.session.commit()

        return send_response(rental_fee, 200)


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

        rented_books = RentedHistory.query.filter(
            RentedHistory.start_date >= start,
            RentedHistory.start_date <= end,
            or_(
                RentedHistory.end_date <= end,
                RentedHistory.end_date.is_(None),
            ),
        ).all()



        if return_type.lower() == "list":
            data = []
            for instance in rented_books:
                book = instance.book
                data.append(to_dict(book))
            return data
        return rented_books
    
    
    def calculate_total_rental_fee(self, start_date, end_date):

        #1.Find all books that have been rented on a specific period
        rented_books = self.get_all_rented_books_for_period(start_date,end_date,'instances')

        #2. Calculate total revenue for this specific range
        total = sum(book.total_cost for book in rented_books)
        return total
        
    