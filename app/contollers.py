from app.models import Book, User,RentedHistory
from app.general import days_between
import datetime
from sqlalchemy import func


class BookService:
    # def __init__(self, session: Session):
    #     self.session = session

    def get_all_books(self):
        data = Book.query.filter_by(isAvailable=True).all()
        data = [book.to_dict() for book in data]
        return data


    def get_book_by_identifier(self, identifier:str,value):


        if identifier.lower() == 'isbn':
            data = Book.query.get(value)
            data = data.to_dict()
        else:
            data = Book.query.filter_by(**{identifier: value}).all()
            data = [book.to_dict() for book in data]

        return data


    def is_available_for_rent(self,id):
        book = Book.query.get(id)
        if book and book.isAvailable:
            print(f"Book with is available.")
            return book
        else:
            print(f"Book with is not available or does not exist.")
            return False


    def rent_book(self,book,db):

        book.isAvailable = False
        print('Book Availability updated successfully!')

        #Create new timestamp
        date = datetime.datetime.now()

        # Format as "YYYY-MM-DD"
        formatted_date = date.strftime('%Y-%m-%d')

        #check if book is already inserted on the list of history table
        rentedBook =  RentedHistory.query.get(book.isbn)

        if rentedBook:
            rentedBook.start_date = formatted_date
            print('Rented book date updated successfully!')
        else:
            # Create an instance of RentedHistory
            new_rented_book = RentedHistory(
                isbn = book.isbn,  # Replace with a valid ISBN
                total_cost = 0,
                start_date = formatted_date,
                end_date = None
            )

            # Add the instance to the session
            db.session.add(new_rented_book)

            print('Created new instance for rented book successfully!')


        db.session.commit()
        


class UserService:
    # def __init__(self, session: Session):
    #     self.session = session

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



class HistoryService:
    def get_rented_book(self,value):

        #Later find rented book by user-id and isbn - NOW USE ONLY ISBN - BE CAREFUL ISBN CAN BE FOUND MORE THAT 1 TIME ON THIS TABLE
        data = RentedHistory.query.filter_by(isbn = value).first()
        if data: return data 
        return None


    def calculate_rental_fee(self,start,end):
   
        print(start,end)

        days = days_between(start,end)
        print(days)

        if days <= 3:
            return days*1
        else:
            return 3*1 + (days-3)*0.5
        
    
    def calculate_total_rental_fee(self):
     return RentedHistory.query.with_entities(func.sum(RentedHistory.total_revenue)).scalar()


    def return_book(self, rentedBook, db):
        # 1.Change Availability on Book table to True
        book = rentedBook.book
        book.isAvailable = True

        # 2.C Update end_date for current book

        date = datetime.datetime.now()      
        end_date = date.strftime('%Y-%m-%d')

        rentedBook.end_date = end_date

        #2.Calculate rental fee based on rented days
        rental_fee = self.calculate_rental_fee(rentedBook.start_date,end_date)


        #3. Update total revenue for current book
        rentedBook.total_cost = rental_fee

        db.session.commit()


        #4. Update user with rental fee he/she has to pay for the book
        return rental_fee
    

    def get_all_rented_books_for_period(self, start, end, return_type):
        rented_books = RentedHistory.query.filter(RentedHistory.start_date.isnot(None), 
                                                  RentedHistory.end_date.isnot(None),
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
        total = sum(book.total_cost for book in rented_books)
        return total
        
    