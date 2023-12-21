import os
from datetime import datetime, timedelta
import jwt
from flask import jsonify, make_response
from app.models import RentedHistory, User
from app.utilities import to_dict, send_response


class UserService:

    def get_user_by_id(self, user_id):
        """
            Retrieve user information and their rented books based on the given user_id.

            Parameters:
            - user_id (int): The unique identifier of the user.

            Returns:
            - dict: A json response containing user information and a list of rented books.

            Raises:
            - HTTPException: If the user with the specified user_id is not found,
             a 404 error is returned.
        """

        # 1. Find current user
        user = User.query.get(user_id)

        if not user:  # User doesn't exists
            return send_response("User not found", 404)

        data = to_dict(user)

        # 2. Find all rentals for this specific user on history table
        rented_books = RentedHistory.query.filter_by(user=user_id, end_date=None)

        rented_books_info = []
        # 3. For each rental get book info based on foreign key isbn
        for rented_instance in rented_books:
            rented_books_info.append(to_dict(rented_instance.book))

        # 4. Format return data with rented books
        data['rented_books'] = rented_books_info

        return send_response(data)

    def create_user(self, json_data: dict, db):

        """
        Create a new user with the provided user data and add it to the database.

        Parameters:
        - json_data (dict): A dictionary containing user data,
         including 'username', 'email', and 'password'.
        - db: The database session to interact with.

        Returns:
        - dict: A response message indicating the result of the user creation process.

        Raises:
        - HTTPException: If the provided username or email already exists, a 409 error is returned.
        """

        username, email, password = json_data.values()

        already_user = User.query.filter(User.username == username,
                                         User.email == email).first()

        if already_user:
            return send_response("Username or email already exists", 409)

        new_user = User(username, email, password)

        db.session.add(new_user)
        db.session.commit()

        return send_response("User created successfully", 201)

    def login(self, credentials: dict):

        """
        Authenticate a user with the provided credentials and
         generate a JWT token upon successful authentication.

        Parameters:
        - credentials (dict): A dictionary containing user login credentials, including 'email' and 'password'.

        Returns:
        - response: A json response with JWT token and user data.

        Raises:
        - HTTPException: If the provided credentials are incomplete or invalid, a 401 error is returned.
        - HTTPException: If the user with the specified email is not found, a 404 error is returned.

        """

        if not credentials or not credentials.get('email') or not credentials.get('password'):
            return send_response("Could not verify", 401)

        # 1. Get data from json request
        email, password = credentials.values()

        # 2. Find current user on the system
        user = User.query.filter_by(email=email).first()

        # 3. Check for user existence - if not return 404
        if not user:
            return send_response("User not found", 404)

        # 4. Check for valid credentials from user - if not return 401
        if not user.check_password(password):
            return send_response("Invalid credentials", 401)

            # 5. OK ready to login and create new JWT for user
        return self.generate_token(user.id)

    def generate_token(self, user_id: int):

        """
        Generate a JWT token for the specified user_id.

        Parameters:
        - user_id (int): The unique identifier of the user for whom the token is generated.

        Returns:
        - response: A json response with JWT token and user data.

        """

        token = jwt.encode({
            "user_id": user_id,
            "expiration": str(datetime.utcnow() + timedelta(seconds=120))
        }, os.getenv('SECRET_KEY'))

        response = jsonify({
            "message": "Login successful",
            "access_token": token,
            "token_type": "Bearer"
        })

        return make_response(response, 200)
