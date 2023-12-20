
from app.utilities import is_date_args_valid as checkArgs


def test_valid_dates():
    args_list = {'start': '2023-01-01', 'end': '2023-01-31'}
    result = checkArgs(args_list)
    assert result == ['2023-01-01', '2023-01-31']

def test_invalid_dates():
    # Case: start date is missing
    args_list = {'end': '2023-01-31'}
    result = checkArgs(args_list)
    assert result == []

    # Case: end date is missing
    args_list = {'start': '2023-01-01'}
    result = checkArgs(args_list)
    assert result == []
    
    # Case: both dates are missing
    args_list = {}
    result = checkArgs(args_list)
    assert result == []

    # Case: start date is after end date
    args_list = {'start': '2023-01-31', 'end': '2023-01-01'}
    result = checkArgs(args_list)
    assert result == []

def test_dates_edge_cases():
    # Case: both dates are the same
    args_list = {'start': '2023-01-01', 'end': '2023-01-01'}
    result = checkArgs(args_list)
    assert result == ['2023-01-01', '2023-01-01']

    # Case: valid dates with additional parameters
    args_list = {'start': '2023-01-01', 'end': '2023-01-31', 'extra': 'value'}
    result = checkArgs(args_list)
    assert result == ['2023-01-01', '2023-01-31']


from app.utilities import user_data_is_valid

def test_user_valid_data():
    data = {'username': 'john_doe', 'email': 'john@example.com', 'password': 'password123'}
    result = user_data_is_valid(data)
    assert result is True

def test_user_invalid_data():

    # Case - 1 Missing username
    data = {'email': 'john@example.com', 'password': 'password123'}
    result = user_data_is_valid(data)
    assert result is False

    # Case - 2 Missing email
    data = {'username': 'john_doe', 'password': 'password123'}
    result = user_data_is_valid(data)
    assert result is False

    # Case - 3 Missing password
    data = {'username': 'john_doe', 'email': 'john@example.com'}
    result = user_data_is_valid(data)
    assert result is False

    # Case - 4 No data at all
    data = {}
    result = user_data_is_valid(data)
    assert result is False

    # Case - 4 Extra data provided
    data = {'username': 'john_doe', 'email': 'john@example.com', 'password': 'password123', 'extra': 'value'}
    result = user_data_is_valid(data)
    assert result is True
