from main import create_app

app = create_app()
client = app.test_client()

#Test books route
def test_get_all_books():

    # Simulate a GET request to /books
    response = client.get('/books')

    # Check that the response status code is 200 (OK)
    assert response.status_code == 200

    data = response.get_json()

    # Check that the returned JSON
    assert isinstance(data, dict)
    assert 'data' in data

    assert 'status code' in data
    assert 'status' in data

    # Check if the list is not empty
    assert len(data['data']) > 480

#Test author route
def test_get_books_by_author():

    # List of authors to test
    authors_to_test = ["Amy Tan", "Celia Brooks Brown", "Mordecai Richler","Jo Dereske"]

    for author_name in authors_to_test:
        # Simulate a GET request to /author/{author}
        response = client.get(f'/author/{author_name}')

        # Check that the response status code is 200 (OK)
        assert response.status_code == 200

        data = response.get_json()

        assert 'data' in data  
        assert isinstance(data['data'], list) 

        # Example: Check that each book has an 'author' key with the expected value
        for book in data['data']:
            assert 'author' in book
            assert book['author'] == author_name

#Test publisher route
def test_get_books_by_publisher():

    # List of publishers to test
    publishers_to_test = ["Avon", "Fireside", "Berkley Publishing Group","Gallimard"]

    for publisher in publishers_to_test:
        response = client.get(f'/publisher/{publisher}')

        # Check that the response status code is 200 (OK)
        assert response.status_code == 200

        data = response.get_json()

        assert 'data' in data  
        assert isinstance(data['data'], list) 

        for book in data['data']:
            assert 'publisher' in book
            assert book['publisher'] == publisher
        

def test_get_rentals_invalid():

    #------------------- Invalid dates ------------------------
    # Assuming you have invalid start_date and end_date parameters
    start_date = "2023-01-01"
    end_date = "2023-02-31"

    response = client.get(f'/rentals?start={start_date}&end={end_date}')
    assert response.status_code == 404

    data = response.get_json()

    assert 'message' in data  
    assert 'status' in data  

    assert data['status'] == 'error'
    assert data['message'] == 'No data available'


def test_get_rentals_valid():

    #------------------- Valid dates ------------------------

    # Assuming you have valid start_date and end_date parameters
    start_date = "2023-12-15"
    end_date = "2023-12-31"

    response = None
    response = client.get(f'/rentals?start={start_date}&end={end_date}')
    assert response.status_code == 200

    data = response.get_json()

    assert 'data' in data  
    assert isinstance(data['data'], list) 

    assert 'status' in data  
    assert data['status'] == 'success'

    # Check if the list is not empty
    assert len(data['data']) > 0


def test_get_total_revenue_valid_dates():

    # Assuming you have valid start_date and end_date parameters
    start_date = "2023-12-15"
    end_date = "2023-12-31"

    response = client.get(f'/revenue?start={start_date}&end={end_date}')
    assert response.status_code == 200

    data = response.get_json()

    assert 'data' in data 
    assert 'status' in data and data['status'] == 'success'
    assert 'status code' in data and data['status code'] == 200


def test_get_total_revenue_invalid_dates():
    # Assuming you have invalid start_date and end_date parameters
    start_date = "2023-01-01"
    end_date = "2023-02-31"

    response = client.get(f'/revenue?start={start_date}&end={end_date}')
    assert response.status_code == 404

    data = response.get_json()

    assert 'message' in data and data['message'] == 'No data available'
    assert 'status' in data and data['status'] == 'error'
    assert 'status code' in data and data['status code'] == 404
