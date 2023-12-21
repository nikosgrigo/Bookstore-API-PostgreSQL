from app.models import Book, RentedHistory
from app.utilities import to_dict, send_response
from datetime import datetime


class BookService:

    def get_all_books(self):
        """
        Retrieve information about all available books.

        Returns:
        - list: A list of dictionaries containing information about available books.

        """

        data = Book.query.filter_by(isAvailable=True).all()
        data = [to_dict(book) for book in data]
        return data

    def get_book_by_identifier(self, identifier: str, value):
        """
        Retrieve books based on the specified identifier and value.

        Parameters:
        - identifier (str): The identifier to search for books, either 'isbn' or another attribute.
        - value: The value corresponding to the specified identifier.

        Returns:
        - dict or list: A dictionary containing information about a single book if identifier is 'isbn,'
          or a list of dictionaries containing information about multiple books if identifier is another attribute.
        """

        if identifier.lower() == 'isbn':
            book = Book.query.get(value)
            data = to_dict(book) if book else None
        else:
            data = Book.query.filter_by(**{identifier: value}).all()
            data = [to_dict(book) for book in data] if data else None
        return data

    def rent_book(self, db, user_id, book_id: str):

        """
        Rent a book for a specified user and update related records in the database.

        Parameters:
        - db: The database session to interact with.
        - user_id (int): The unique identifier of the user renting the book.
        - book_id (str): The unique identifier of the book to be rented.

        Returns:
        - None
        """

        book = Book.query.get(book_id)

        # Check if book exists and if it is available for rent
        if not book or not book.isAvailable:
            return send_response("Book not available for rent", 400)

        book.isAvailable = False

        # Create new timestamp
        date = datetime.now()

        # Format as "YYYY-MM-DD"
        formatted_date = date.strftime('%Y-%m-%d')

        # Create new instance on History table
        new_rented_book = RentedHistory(0, formatted_date, None, book.isbn, user_id)

        # Add the instance to the session
        db.session.add(new_rented_book)
        db.session.commit()

        return send_response("Book rented successfully", 200)
