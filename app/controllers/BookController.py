from app.models import Book,RentedHistory
from app.utilities import to_dict,send_response
from datetime import datetime

class BookService:

    def get_all_books(self):

        '''
        Get all available books from the database.

        Returns:
        - list: A list of dictionaries containing information about each available book.

        '''

        data = Book.query.filter_by(isAvailable=True).all()
        data = [to_dict(book) for book in data]
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
            book = Book.query.get(value)
            data = to_dict(book) if book else None
        else:
            data = Book.query.filter_by(**{identifier: value}).all()
            data = [to_dict(book) for book in data] if data else None
        return data


    def rent_book(self, db, user_id, book_id):

        book = Book.query.get(book_id)

        # Check if book exists and if it is available for rent
        if not book or not book.isAvailable:
            return send_response("Book not available for rent", 400)
        

        book.isAvailable = False

        #Create new timestamp
        date = datetime.now()      

        # Format as "YYYY-MM-DD"
        formatted_date = date.strftime('%Y-%m-%d')

        # Create new instance on History table
        new_rented_book = RentedHistory(0,formatted_date,None,book.isbn,user_id)

        # Add the instance to the session
        db.session.add(new_rented_book)
        db.session.commit()

        return send_response("Book rented successfully", 200)
        

