import pytest
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def get_access_token(client_id, client_secret, refresh_token):
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': "refresh_token",
        'f': 'json'
    }
    response = requests.post(auth_url, data=payload, verify=False)
    access_token = response.json()['access_token']
    return access_token

def fetch_strava_activities(access_token, start_date=None):
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    header = {'Authorization': 'Bearer ' + access_token}
    
    # Convert start_date to Unix timestamp if it's not None
    if start_date:
        start_date_unix = int(start_date.timestamp())
        params['after'] = start_date_unix

    activities_response = requests.get(activities_url, headers=header, params=params).json()
    return activities_response

def test_fetch_activities():
    client_id = os.getenv('CLIENT_ID_2')
    client_secret = os.getenv('CLIENT_SECRET_2')
    refresh_token = os.getenv('REFRESH_TOKEN_2')

    # Get the access token
    access_token = get_access_token(client_id, client_secret, refresh_token)
    assert access_token is not None, "Failed to obtain access token."

    # Fetch the athlete and activities data
    activities_data = fetch_strava_activities(access_token)
    
    # Assert that activities data is fetched successfully
    assert activities_data is not None, "No activities found or there was an error fetching activities."
    assert len(activities_data) > 0, "No activities were returned."
