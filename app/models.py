
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    isAdmin = db.Column(db.Boolean, default=False)


class RentedHistory(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   
    total_cost = db.Column(db.Integer)
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String)

    isbn = db.Column(db.String, db.ForeignKey('books.isbn'), nullable=False)
    user = db.Column(db.Integer ,db.ForeignKey('users.id'), nullable=False)

    # Define the relationships
    book = db.relationship('Book', backref='rented_histories', foreign_keys=[isbn])
    user_info = db.relationship('User', backref='rented_histories', foreign_keys=[user])

    def __init__(self, total_cost, start_date, end_date, isbn, user):
        self.total_cost = total_cost
        self.start_date = start_date
        self.end_date = end_date
        self.isbn = isbn
        self.user = user

    def to_dict(self):
        """Convert the Book instance to a dictionary."""
        return {
            'id': self.id,
            'isbn': self.isbn,
            'total_cost': self.total_cost,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
    

class Book(db.Model):
    __tablename__ = 'books'

    isbn = db.Column(db.String, primary_key=True, nullable=False)
    
    title = db.Column(db.String)
    author = db.Column(db.String)
    year_of_publication = db.Column(db.Integer)
    publisher = db.Column(db.String)

    
    image_url_s = db.Column(db.String)
    image_url_m = db.Column(db.String)
    image_url_l = db.Column(db.String)

    rented_now = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    isAvailable = db.Column(db.Boolean, default=True)


    def __init__(self, isbn, title, author, year_of_publication, publisher,
                 image_url_s, image_url_m, image_url_l, rented_now, rating, isAvailable=True):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year_of_publication = year_of_publication
        self.publisher = publisher
        self.image_url_s = image_url_s
        self.image_url_m = image_url_m
        self.image_url_l = image_url_l
        self.rented_now = rented_now
        self.rating = rating
        self.isAvailable = isAvailable




    def to_dict(self):
        """Convert the Book instance to a dictionary."""
        return {
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'year_of_publication': self.year_of_publication,
            'publisher': self.publisher,
            'image_url_s': self.image_url_s,
            'image_url_m': self.image_url_m,
            'image_url_l': self.image_url_l,
        }