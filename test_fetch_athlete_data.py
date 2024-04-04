import pytest
import requests
from unittest.mock import patch, MagicMock


def fetch_athlete_data(access_token):
    athlete_url = "https://www.strava.com/api/v3/athlete"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(athlete_url, headers=headers)
    athlete_data = response.json()
    return athlete_data

# Mock test for fetch_athlete_data
@patch('requests.get')
def test_fetch_athlete_data(mock_get):
    # Setup mock
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'id': 12345,
        'username': 'test_user',
        # Add more fields as needed
    }
    mock_get.return_value = mock_response

    # Call the function with a mock access token
    athlete_data = fetch_athlete_data("mock_access_token")

    # Assertions to verify the expected outcome
    assert athlete_data['id'] == 12345
    assert athlete_data['username'] == 'test_user'
    # Add more assertions as needed

    # Verify the requests.get call was made as expected
    mock_get.assert_called_once_with("https://www.strava.com/api/v3/athlete", headers={'Authorization': 'Bearer mock_access_token'})
