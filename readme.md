# Bookstore API

## Overview

This is a Python Flask API for a bookstore, utilizing PostgreSQL and SQLAlchemy for data storage.

## Prerequisites

Make sure you have the following installed:

- Python 3.x
- Flask
- Flask-SQLAlchemy
- Psycopg2 
- PostgreSQL
- SQLAlchemy
- Pandas
- Pytest 
- PyJWT 

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/nikosgrigo/Bookstore-API-PostgreSQL.git
    cd Bookstore-API-PostgreSQL
    ```

2. Install dependencies from Prerequisites


## Configuration

1. Create a PostgreSQL database.

2. Create a `config.ini` file inside config module/folder.

3. Update `config.ini` with your database credentials:

    ```python
    # config.ini

        ; Database Configuration

        [Database]
        ; Database connection settings
        dialect = postgresql
        driver = psycopg2
        db_username = ...
        password = ...
        host = localhost
        port = ...
        db_name = ...
        secret_key = ...

        [DatabaseURL]
        ; Database URL
        connection_db_string = {dialect}+{driver}://{db_username}:{password}@{host}:{port}/{db_name}
    ```

## Running the API
1. Start server
2. Start the Flask application:

```bash
python main.py
```

## Testing

1. change path to '../config/config.ini' (config/Config.py at method __init__)
2. cd tests
3. run pytest

```bash
pytest
```

## API Endpoints

1. /books,                 GET
2. /book/<id>,             GET
3. /author/<author>,       GET
4. /publisher/<publisher>, GET
5. /date/<date>,           GET
6. /rent/<book_id>,        POST     (Admin)
7. /return/<book_id>,      PUT      (Admin)
8. /rentals                GET      (Admin)
9. /revenue                GET      (Admin)
10. /user                  POST
11. /users/<id>            GET      (Admin)
12. /login                 POST
13. /backup                GET      (Admin)