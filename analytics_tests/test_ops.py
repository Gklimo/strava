# Unit tests
from dagster import build_op_context
from unittest.mock import patch, MagicMock
from analytics.ops.strava import get_access_token, fetch_athlete_data


def test_fetch_athlete_data():
    access_token = "fake_access_token"
    mock_response = {
        "id": 12345,
        "username": "testathlete",
        # Include other relevant fields for your mock response
    }
    
    context = build_op_context()
    
    # Mock the requests.get call within fetch_athlete_data to return
    # mock_response when called with the Strava API URL and headers.
    with patch('analytics.ops.strava.requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_response
        result = fetch_athlete_data(context, access_token)
        
        assert result == mock_response

@patch('requests.post')
def test_get_access_token(mock_post):
    # Mock response from the Strava API
    mock_response = MagicMock()
    mock_response.json.return_value = {'access_token': 'fake_access_token'}
    mock_post.return_value = mock_response

    # Define dummy client_id, client_secret, and refresh_token
    client_id = "1234567890"
    client_secret = "abcdef123456"
    refresh_token = "refresh_token_here"

    # Call the operation
    access_token = get_access_token(client_id, client_secret, refresh_token)

    # Assert that the requests.post method was called with the correct arguments
    mock_post.assert_called_once_with(
        "https://www.strava.com/oauth/token",
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': "refresh_token",
            'f': 'json'
        },
        verify=False
    )

    # Assert the operation returns the expected access token
    assert access_token == 'fake_access_token', "The access token returned does not match the expected value."
