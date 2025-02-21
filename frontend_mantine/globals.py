import os
import pandas as pd 
import requests
from flask import session
from datetime import datetime, timedelta, timezone

# from dotenv import load_dotenv
# load_dotenv()

directory_= os.getcwd()


SHOP_RELATIVE_PATH = '/'
DASH_URL_BASE_PATHNAME = '/building_benchmarking/'
os.environ['DASH_URL_BASE_PATHNAME'] = DASH_URL_BASE_PATHNAME


username_shops = os.getenv('USERNAME_SHOPS', '')
password_shops = os.getenv('PASSWORD_SHOPS', '')
url_shops = os.getenv('URL_SHOPS', '')
url_api_data_metadata = os.getenv('URL_API_DATA_METADATA', "http://127.0.0.1:8000")

# Shops authentication token is valid for 120 minutes
SHOPS_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('SHOPS_ACCESS_TOKEN_EXPIRE_MINUTES', 120))


def get_token_auth_shops(url_shops, username, password):
    '''
    Authenticate and retrieve an access token from the shops API.

    Parameters
    ----------
    url_shops : str
        Base URL of the shops API (e.g., "api.example.com").
    username : str
        Client ID or username for authentication.
    password : str
        Secret or password associated with the client ID.

    Returns
    -------
    str
        The access token retrieved from the API response.
    '''
    token = None

    # Construct the URL for the authentication endpoint, including the username and password as query parameters.
    url = f"{url_shops}/store_data/api/v1/token?clientID={username}&secret={password}"
    
    # Send a POST request to the authentication endpoint and parse the JSON response.
    response = requests.request("POST", url).json()
    
    # Extract and return the access token from the JSON response.
    if 'access_token' in response: 
        token = response['access_token']

    return token


def get_building_list_global() -> pd.DataFrame:
    '''
    Get list of buildings stored in the TTL file.

    This function sends a GET request to an API endpoint to retrieve a list of buildings
    and returns the result as a pandas DataFrame.
    '''
    # Construct the API endpoint URL using the base URL
    url = f"{url_api_data_metadata}/moderate/api/v1/building_list"

    # Empty payload and headers for the request
    payload = {}
    headers = {}

    # Send a GET request to the API and store the response
    response = requests.request("GET", url, headers=headers, data=payload)

    # Convert the JSON response into a pandas DataFrame
    building = pd.DataFrame(response.json())

    # Rename the single column of the DataFrame to 'Buis' (possible typo, check naming intention)
    building.columns = ['Buis']

    # Return the DataFrame with the list of buildings
    return building



def get_shops_api_token():
    token = None
    token_expire = datetime.min.replace(tzinfo=timezone.utc)
    
    if 'shops_api_token' in session:
        token = session['shops_api_token']
        token_expire = session['shops_api_token_expire']

    if token is None or datetime.now(timezone.utc) > token_expire:
        token = get_token_auth_shops(url_shops, username_shops, password_shops)
        if token is not None:
            session['shops_api_token'] = token
            session['shops_api_token_expire'] = datetime.now(timezone.utc) + timedelta(minutes=SHOPS_ACCESS_TOKEN_EXPIRE_MINUTES-1) # one minute before token expire

    return token