from flask import request,Blueprint
from app.utilities import *
from app.models import db
from app.controllers import BookController,UserController,HistoryController


main_app = Blueprint('main', __name__)

BookService = BookController.BookService()
HistoryService = HistoryController.HistoryService()
UserService = UserController.UserService()

# Retrieve a list of all available books
@main_app.route('/books',methods = ['GET'])
def get_all_books():
   data = BookService.get_all_books()
   return send_response(data)


# Retrieve a list of available books based on a specified category.
@main_app.route('/author/<author>',methods = ['GET'])
def get_books_by_author(author):
   data = BookService.get_book_by_identifier('author',author)
   return send_response(data)
   
               
# Retrieve detailed information about a specific book.
@main_app.route('/book/<id>',methods = ['GET'])
def get_books_by_id(id):
   data = BookService.get_book_by_identifier('isbn',id)
   return send_response(data)


# Retrieve a list of available books that was released by a specific publisher
@main_app.route('/publisher/<publisher>', methods = ['GET'])
def get_books_by_publisher(publisher):
   data = BookService.get_book_by_identifier('publisher',publisher)
   return send_response(data)


#Retrieve a list of available books that was released on a specific year or between certain dates (e.g., from 2000 to 2005)
@main_app.route('/date/<date>', methods = ['GET'])
def get_books_by_date(date):
   data = BookService.get_book_by_identifier('year_of_publication',date)
   return send_response(data)


#Rent a book, making it unavailable for others to rent.
@main_app.route('/rent/<book_id>', methods = ['POST'])
@token_required
def set_book_as_rented(user,book_id):
   return BookService.rent_book(db, user['id'], book_id)


# Return a rented book and calculate the rental fee based on the number of days rented.
@main_app.route('/return/<book_id>', methods = ['PUT'])
@token_required
def get_rented_book(user, book_id):
   
   if not user['isAdmin']:
      return send_response("Oops you do not have the permission to access this resource.",403)

   return HistoryService.return_book(db, book_id)


# Retrieve a list of books that were rented within a specified date range.    
@main_app.route('/rentals',methods = ['GET'])
@token_required
def get_rentals(user):

   valid_dates = is_date_args_valid(request.args)

   if not valid_dates:
      return send_response("Please provide valid dates", 400)
   
   if not user['isAdmin']:
      return send_response("Oops you do not have the permission to access this resource.", 403)
   
   start_date,end_date = valid_dates

   data = HistoryService.get_all_rented_books_for_period(start_date,end_date,'list')

   export_to_csv(data,"Rentals")
      
   return send_response(data) 


#Calculate and retrieve the total revenue generated by book rentals within a specified date range. 
@main_app.route('/revenue',methods = ['GET'])
@token_required
def get_total_revenue(user):

   valid_dates = is_date_args_valid(request.args)
   
   if not valid_dates:
      return send_response("Please provide valid dates", 400)
   
   if not user['isAdmin']:
      return send_response("Oops you do not have the permission to access this resource.", 403)
   
   start_date,end_date = valid_dates

   # Calculate total revenue for this specific range
   data = HistoryService.calculate_total_rental_fee(start_date, end_date)

   export_to_csv(data,"TotalRevenue")
      
   return send_response(data) 


#Create a new user account    
@main_app.route('/user',methods = ['POST'])
def create_new_user():

   #1. Get user data from json 
   data = request.json

   #2. Check if required fields are valid and present
   if not user_data_is_valid(data):
      send_response("Invalid request body", 400) 

   return UserService.create_user(data, db)


#Retrieve information about a specific user    
@main_app.route('/users/<id>',methods = ['GET'])
@token_required
def get_user(user, id):

   if not user['isAdmin']:
      return send_response("Oops you do not have the permission to access this resource.", 403)
   
   return UserService.get_user_by_id(id)


@main_app.route('/login',methods = ['POST'])
def login():
   
   #1. Get user credentials from json 
   auth = request.json

   return UserService.login(auth)


# create a backup csv with the current state of the users database.
@main_app.route('/backup',methods = ['GET'])
@token_required
def get_backup(user):

   if not user['isAdmin']:
      return send_response("Oops you do not have the permission to access this resource.", 403)

   return send_response('Back up successfully created', 200) if backup() else send_response('Back up could not be created', 404)
   


