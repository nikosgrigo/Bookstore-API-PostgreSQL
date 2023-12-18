from app.models import *
import pandas as pd
import datetime
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


    def rent_book(self,book,db):

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
        date = datetime.datetime.now()

        # Format as "YYYY-MM-DD"
        formatted_date = date.strftime('%Y-%m-%d')

        #--------ONLY FOR DEVELOPEMENT PURPOSES--------
        userId = 1
        #--------ONLY FOR DEVELOPEMENT PURPOSES--------


        new_rented_book = RentedHistory(0,formatted_date,None,book.isbn,userId)

        # Add the instance to the session
        db.session.add(new_rented_book)
        print('Created new instance for rented book successfully!')
        db.session.commit()

        status_code = 200
        response = jsonify({"message": "Book rented successfully", "status": "success", "status code":status_code})
        return make_response(response, status_code)
        

class HistoryService:

    def get_rented_book(self,book_id):

        '''
        Get information about a rented book based on its rented ID.

        Parameters:
        - rented_id: The rented ID of the book.

        Returns:
        - The rented book information if found, None otherwise.

        '''

        userID = 1

        data = RentedHistory.query.filter_by(isbn = book_id, user = userID).first()
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
    

    def return_book(self, rentedBook, db):

        '''
        Return a rented book, update book availability, and record the return transaction in the rented history.

        Parameters:
        - rentedBook: The rented book instance to be returned.
        - db: The SQLAlchemy database instance.

        Returns:
        - float: The calculated rental fee for the returned book.

        '''

        if not rentedBook:
            status_code = 400
            response = jsonify({"message": "Book not found or not currently rented", "status": "error", "status code":status_code})
            return make_response(response, status_code)

        # 1. Change Availability on Book table to True using foreign key
        book = rentedBook.book
        book.isAvailable = True

        # 2. Update end_date for current book

        date = datetime.datetime.now()      
        end_date = date.strftime('%Y-%m-%d')

        rentedBook.end_date = end_date

        #3. Calculate rental fee based on rented days
        rental_fee = self.calculate_rental_fee(rentedBook.start_date,end_date)


        #4. Update total_cost on the instance
        rentedBook.total_cost = rental_fee

        db.session.commit()

        status_code = 200
        response = jsonify({"message": "Book returned successfully","rental_fee":rental_fee, "status": "success", "status code":status_code})
        return make_response(response, status_code)

    
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

        rented_books = RentedHistory.query.filter(RentedHistory.end_date.isnot(None),
                                                  RentedHistory.start_date >= start,
                                                  RentedHistory.end_date <= end).all()
        

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
        
    
class UserService:


    def get_all_users(self):
        data = User.query().all()
        data = [book.to_dict() for book in data]
        return data


    def get_user_by_id(self, id):
        data = User.query.get(id)
        return data.to_dict()


    def create_user(self, json_data, db):

        username, email, password, isAdmin = json_data.values()
        isAdmin = bool(isAdmin)

        if not self.check_if_user_exists(username, email):       #Check if user already exists

            new_user = User(username = username,
                             email = email,
                             password = password,
                             isAdmin = isAdmin
                             )
            db.session.add(new_user)
            db.session.commit()
            return True
        return False


    def check_if_user_exists(self, username, email):
        data = User.query.filter(User.username == username, User.email == email).first()
        
        return True if data else False