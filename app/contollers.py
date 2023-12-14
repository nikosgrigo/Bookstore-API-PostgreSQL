from app.models import *
from app.general import days_between
import datetime


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
            return data.to_dict() if data else None
        else:
            data = Book.query.filter_by(**{identifier: value}).all()
            return [book.to_dict() for book in data] if data else None


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


        book.isAvailable = False
        print('Book Availability updated successfully!')

        #Create new timestamp
        date = datetime.datetime.now()

        # Format as "YYYY-MM-DD"
        formatted_date = date.strftime('%Y-%m-%d')

        #check if book is already inserted on the list of history table
        rentedBook =  RentedHistory.query.get(book.isbn)

        #--------ONLY FOR DEVELOPEMENT PURPOSES--------
        userId = 1
        #--------ONLY FOR DEVELOPEMENT PURPOSES--------

        if rentedBook:
            rentedBook.start_date = formatted_date
            print('Rented book date updated successfully!')
        else:
            # Create an instance of RentedHistory
            new_rented_book = RentedHistory(
                total_cost = 0,
                start_date = formatted_date,
                end_date = None,
                isbn = book.isbn,
                user = userId
            )

            # Add the instance to the session
            db.session.add(new_rented_book)

            print('Created new instance for rented book successfully!')


        db.session.commit()
        

class HistoryService:

    def get_rented_book(self,rented_id):

        '''
        Get information about a rented book based on its rented ID.

        Parameters:
        - rented_id: The rented ID of the book.

        Returns:
        - The rented book information if found, None otherwise.

        '''

        data = RentedHistory.query.get(int(rented_id))
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

        days = days_between(start,end)

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

        return rental_fee
    

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
        
    