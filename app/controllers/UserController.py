
from app.models import Book,RentedHistory,User
from flask import jsonify, make_response
from datetime import datetime, timedelta
import os,jwt


class UserService:

    def get_all_users(self):
        data = User.query().all()
        data = [book.to_dict() for book in data]
        return data

    def get_user_by_id(self, id):

        #1. Find current user
        data = User.query.get(id)

        if not data:
            status_code = 404
            response = jsonify({"message": "User not found", "status": "error", "status code":status_code})
            return make_response(response, status_code)


        #2. Find all rentals for this specific user on history table
        rented_books = RentedHistory.query.filter_by(user = id, end_date = None)

        #3. For each rental get book info and insert it into a rented_books list
        rented_books_info = []
        # For each instance, retrieve the corresponding book information
        for rented_instance in rented_books:
            book = Book.query.filter_by(isbn = rented_instance.isbn).first()
            rented_books_info.append(book.to_dict())

        data = data.to_dict(rented_books_info)
    
        status_code = 200
        response = jsonify({"data": data, "status": "success", "status code":status_code})
        return make_response(response, status_code)

    def create_user(self, json_data, db):

        username, email, password = json_data.values()

        already_user = User.query.filter(User.username == username, User.email == email).first()

        if already_user:
            status_code = 409
            response = jsonify({"message": "Username or email already exists", "status": "error", "status code":status_code})
            return make_response(response, status_code)

        new_user = User(username, email, password)

        db.session.add(new_user)
        db.session.commit()

        status_code = 201
        response = jsonify({"message": "User created successfully", "status": "success", "status code":status_code})
        return make_response(response, status_code)

    def login(self, credentials):

        if not credentials or not credentials.get('email') or not credentials.get('password'):
            response = jsonify({"message": "Could not verify", "status": "error", "status code":401})
            return make_response(response, 401)
        
        #1. Get data from json request
        email, password = credentials.values()

        #2. Find current user on the system
        user = User.query.filter_by(email = email).first()

        #3. Check for user existance - if not return 404
        if not user:
            response = jsonify({"message": "User not found", "status": "error", "status code":404})
            return make_response(response, 404)

        #4. Check for valid credentials from user - if not return 401
        if not user.check_password(password):
            response = jsonify({"message": "Invalid credentials", "status": "error", "status code":401})
            return make_response(response, 401)           

        # 5. OK ready to login and create new JWT for user
        return self.generate_token(user.id)

    def generate_token(self, id):
            token = jwt.encode({
                "user_id": id,
                "expiration": str(datetime.utcnow() + timedelta(seconds = 120))
            },os.getenv('SECRET_KEY'))

            response = jsonify({
                                "message": "Login successful",
                                "access_token": token,
                                "token_type": "Bearer"
                                })
            
            return make_response(response, 200) 

        # except jwt.ExpiredSignatureError:
        #     response = jsonify({"message": "Token has expired", "status": "error", "status_code": 401})
        #     return make_response(response, 401)

        # except jwt.InvalidTokenError:
        #     response = jsonify({"message": "Invalid token", "status": "error", "status_code": 401})
        #     return make_response(response, 401)

        # except Exception as e:
        #     response = jsonify({"message": "Login failed", "status": "error", "status_code": 403})
        #     return make_response(response, 403)