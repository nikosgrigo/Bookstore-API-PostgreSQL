from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() 

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    isAdmin = db.Column(db.Boolean, default=False)


class Book(db.Model):
    __tablename__ = 'books'

    isbn = db.Column(db.String, primary_key=True, nullable=False)
    
    title = db.Column(db.String)
    author = db.Column(db.String)
    year_of_publication = db.Column(db.Integer)
    publisher = db.Column(db.String)

    avgrating = db.Column(db.Integer)
    isAvailable = db.Column(db.Boolean, default=True)

    image_url_s = db.Column(db.String)
    image_url_m = db.Column(db.String)
    image_url_l = db.Column(db.String)

    def to_dict(self):
        """Convert the Book instance to a dictionary."""
        return {
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'year_of_publication': self.year_of_publication,
            'publisher': self.publisher,
            'avgrating': self.avgrating,
            'isAvailable': self.isAvailable,
            'image_url_s': self.image_url_s,
            'image_url_m': self.image_url_m,
            'image_url_l': self.image_url_l,
        }


class RentedHistory(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String, db.ForeignKey('books.isbn'), nullable=False)
    # user = db.Column(db.String ,db.ForeignKey('users.username'), nullable=False)
    total_cost = db.Column(db.Integer)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)

    # Define the relationships
    book = db.relationship('Book', backref='rented_histories', foreign_keys=[isbn])
    # user_info = db.relationship('User', backref='rented_histories', foreign_keys=[user])

    def to_dict(self):
        """Convert the Book instance to a dictionary."""
        return {
            'id': self.id,
            'isbn': self.isbn,
            'total_cost': self.total_cost,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
    


