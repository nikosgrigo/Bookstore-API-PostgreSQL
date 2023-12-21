from app.models import RentedHistory
from app.utilities import to_dict, send_response
import pandas as pd
from datetime import datetime
from sqlalchemy import or_


class HistoryService:

    def calculate_rental_fee(self, start: str, end: str):

        """
        Calculate the rental fee based on the given start and end dates.

        Parameters:
        - start (str): The start date of the rental in the format '%Y-%m-%d'.
        - end (str): The end date of the rental in the format '%Y-%m-%d'.

        Returns:
        - float: The calculated rental fee.
        """

        dt0 = pd.to_datetime(start, format='%Y-%m-%d')
        dt1 = pd.to_datetime(end, format='%Y-%m-%d')
        days = (dt1 - dt0).days

        if days <= 3:
            return days * 1
        return 3 * 1 + (days - 3) * 0.5

    def return_book(self, db, book_id: str):
        """
        Return a rented book and update related records in the database.

        Parameters:
        - db: The database session to interact with.
        - book_id (str): The unique identifier of the book to be returned.

        Returns:
        - dict: A response message indicating the result of the book return process.

        """

        # 1. Find book on history table based on isbn and user-id
        rentedBook = RentedHistory.query.filter(
            RentedHistory.isbn == book_id,
            RentedHistory.end_date.is_(None),
        ).first()

        if not rentedBook:
            return send_response("Book not found or not currently rented", 400)

        # 2. Change Availability on Book table to True using foreign key
        book = rentedBook.book
        book.isAvailable = True

        # 3. Update end_date for current book
        date = datetime.now()
        end_date = date.strftime('%Y-%m-%d')

        rentedBook.end_date = end_date

        # 4. Calculate rental fee based on rented days
        rental_fee = self.calculate_rental_fee(rentedBook.start_date, end_date)

        # 5. Update total_cost on the instance
        rentedBook.total_cost = rental_fee

        db.session.commit()

        return send_response(rental_fee, 200)

    def get_all_rented_books_for_period(self, start: str, end: str, return_type: str):

        """
        Retrieve all rented books within a specified period.

        Parameters:
        - start (str): The start date of the period in the format '%Y-%m-%d'.
        - end (str): The end date of the period in the format '%Y-%m-%d'.
        - return_type (str): The desired return type, either "list" or the default SQLAlchemy query result.

        Returns:
        - list or SQLAlchemy instance: A list of dictionaries containing book information if return_type is "list,"
          otherwise, the result of the SQLAlchemy query.

        """

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

    def calculate_total_rental_fee(self, start_date: str, end_date: str):

        """
        Calculate the total rental fee for all books rented within a specific period.

        Parameters:
        - start_date (str): The start date of the period in the format '%Y-%m-%d'.
        - end_date (str): The end date of the period in the format '%Y-%m-%d'.

        Returns:
        - float: The total rental fee for all rented books within the specified period.

        """

        # 1.Find all books that have been rented on a specific period
        rented_books = self.get_all_rented_books_for_period(start_date, end_date, 'instances')

        # 2. Calculate total revenue for this specific range
        total = sum(book.total_cost for book in rented_books)
        return total
