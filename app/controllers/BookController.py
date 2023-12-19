from app.models import Book,RentedHistory

from datetime import datetime
from flask import jsonify, make_response

class BookService:

    def get_all_books(self):

        '''
        Get all available books from the database.

        Returns:
        - list: A list of dictionaries containing information about each available book.

        '''

        data = Book.query.filter_by(isAvailable=True).all()
        data = [book.to_dict() for book in data]
        return data

    def get_book_by_identifier(self, identifier:str,value):

        '''
        Get book(s) from the database based on a specified identifier and value.

        Parameters:
        - self: The instance of the class.
        - identifier (str): The identifier to search by (e.g., 'isbn', 'title', 'author').
        - value: The value we are looking for.

        Returns:
        - dict or list: A dictionary or a list of dictionaries containing information about the book(s).

        '''

        if identifier.lower() == 'isbn':
            data = Book.query.get(value)
            data = data.to_dict() if data else None
        else:
            data = Book.query.filter_by(**{identifier: value}).all()
            data = [book.to_dict() for book in data] if data else None
        return data

    def is_available_for_rent(self,id):

        '''
        Check if a book is available for rent based on its ID.

        Parameters:
        - id: The isbn of the book.

        Returns:
        - Book or bool: The book instance if it is available for rent, False otherwise.

        '''

        # Check if book is rented now based on availability
        book = Book.query.get(id)
        if book and book.isAvailable:
            return book
        return False

    def rent_book(self,book,db,user_id):

        '''
        Rent a book, update availability, and record the transaction in the rented history.

        Parameters:
        - book: The book instance to be rented.
        - db: The SQLAlchemy database instance.

        '''

        if not book:
            status_code = 400
            response = jsonify({"message": "Book not available for rent", "status": "error", "status code":status_code})
            return make_response(response, status_code)


        book.isAvailable = False
        print('Book Availability updated successfully!')

        #Create new timestamp
        date = datetime.now()      

        # Format as "YYYY-MM-DD"
        formatted_date = date.strftime('%Y-%m-%d')

        new_rented_book = RentedHistory(0,formatted_date,None,book.isbn,user_id)

        # Add the instance to the session
        db.session.add(new_rented_book)
        print('Created new instance for rented book successfully!')
        db.session.commit()

        response = jsonify({"message": "Book rented successfully", "status": "success", "status code":200})
        return make_response(response, status_code)
        
