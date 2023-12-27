import pytest
from flask import Flask
from app.models import db
from app.routes import main_app
from app.utilities import import_data
from app.controllers.userController import UserService
from app.controllers.historyController import HistoryService
from config.Config import AppConfig

app = Flask(__name__)

config = AppConfig(path = '../config/config.ini')
config.configure_app(app, db)

app.register_blueprint(main_app)

# Create the database tables
with app.app_context():
    try:
        db.create_all()
        import_data(db)
    except Exception as e:
        print('Loading Database and Tables...')


@pytest.fixture
def client():
    client = app.test_client()
    return client

@pytest.fixture
def get_response(client):
    def _get_response(route, expected_status_code=200, check_json=True):
        # Simulate a GET request to the specified route
        response = client.get(route)

        # Check that the response status code matches the expected status code
        assert response.status_code == expected_status_code

        # Check if the response contains JSON data if check_json is True
        if check_json:
            assert response.headers['Content-Type'] == 'application/json'
            assert response.get_json() is not None

        return response.get_json()

    return _get_response


def mock_authorization(user_id:int):
    # Generate a test JWT token
    user = UserService()
    token = user.generate_token(user_id,mode = 'test')
    return token


# Test books route
def test_get_all_books(get_response):
    # Simulate a GET request to /books
    data = get_response('/books')

    # Check that the returned JSON
    assert isinstance(data, dict)
    assert 'data' in data

    assert 'status code' in data
    assert 'status' in data

    # Check if the list is not empty
    assert len(data['data']) > 480


# Test author route
def test_get_books_by_author(get_response):
    # List of authors to test
    authors_to_test = ["Amy Tan", "Celia Brooks Brown", "Mordecai Richler", "Jo Dereske"]

    for author_name in authors_to_test:
        # Simulate a GET request to /author/{author}
        data = get_response(f'/author/{author_name}')

        assert 'data' in data
        assert isinstance(data['data'], list)

        # Example: Check that each book has an 'author' key with the expected value
        for book in data['data']:
            assert 'author' in book
            assert book['author'] == author_name


# Test publisher route
def test_get_books_by_publisher(get_response):
    # List of publishers to test
    publishers_to_test = ["Avon", "Fireside", "Berkley Publishing Group", "Gallimard"]

    for publisher in publishers_to_test:
        data = get_response(f'/publisher/{publisher}')

        assert 'data' in data
        assert isinstance(data['data'], list)

        for book in data['data']:
            assert 'publisher' in book
            assert book['publisher'] == publisher


def test_get_rentals_invalid(client):
    # ------------------- Invalid dates ------------------------
    # Assuming you have invalid start_date and end_date parameters
    start_date = "2023-01-01"
    end_date = "2023-02-31"

    token = mock_authorization(11)
    response = client.get(f'/rentals?start={start_date}&end={end_date}', headers={'x-access-token': token})

    assert response.status_code == 200

    data = response.get_json()

    assert 'status' in data
    assert 'data' in data 
    assert isinstance(data['data'], list)

    assert data['status'] == 'success'
    assert data['data'] == []


def test_get_rentals_valid(client):
    # ------------------- Valid dates ------------------------

    # Assuming you have valid start_date and end_date parameters
    start_date = "2023-12-15"
    end_date = "2023-12-31"

    token = mock_authorization(11)
    response = client.get(f'/rentals?start={start_date}&end={end_date}', headers={'x-access-token': token})

    assert response.status_code == 200

    data = response.get_json()

    assert 'data' in data
    assert isinstance(data['data'], list)

    assert 'status' in data
    assert data['status'] == 'success'

    # Check if the list is not empty
    assert len(data['data']) > 0


def test_get_total_revenue_valid_dates(client):
    # Assuming you have valid start_date and end_date parameters
    start_date = "2023-12-15"
    end_date = "2023-12-31"

    token = mock_authorization(11)

    with app.test_request_context():
        response = client.get(f'/revenue?start={start_date}&end={end_date}', headers={'x-access-token': token})

        assert response.status_code == 200

        data = response.get_json()

        assert 'total revenue' in data
        assert 'status' in data and data['status'] == 'success'
        assert 'status code' in data and data['status code'] == 200

        history = HistoryService()
        expected_result = history.calculate_total_rental_fee(start_date, end_date)

        print(expected_result)
        assert data['total revenue'] == expected_result
    

def test_get_total_revenue_invalid_dates(client):
    # Assuming you have invalid start_date and end_date parameters
    start_date = "2023-01-01"
    end_date = "2023-02-31"

    token = mock_authorization(11)

    with app.test_request_context():
        response = client.get(f'/revenue?start={start_date}&end={end_date}', headers={'x-access-token': token})

        assert response.status_code == 200

        data = response.get_json()

        assert 'total revenue' in data and data['total revenue'] == 0
        assert 'status' in data and data['status'] == 'success'
        assert 'status code' in data and data['status code'] == 200
