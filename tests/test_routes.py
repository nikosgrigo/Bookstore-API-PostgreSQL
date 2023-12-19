from main import create_app

def test_get_all_books():
    app = create_app()
    client = app.test_client()

    # Simulate a GET request to /books
    response = client.get('/books')

    # Check that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assuming the response is a JSON object, you can parse it
    data = response.get_json()

    # Check that the returned JSON
    assert isinstance(data, dict)
    assert 'data' in data

    assert 'status code' in data
    assert 'status' in data

    # Check if the list is not empty
    assert len(data['books']) > 0

    # assert 'title' in data['books'][0]
    # assert 'author' in data['books'][0]

