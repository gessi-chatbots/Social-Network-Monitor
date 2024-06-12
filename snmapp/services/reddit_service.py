import requests
from requests.auth import HTTPBasicAuth


REDDIT_BASE_URL = 'https://oauth.reddit.com'


def reddit_search(query, subreddit='all', limit=10, sort='', token=None):
    endpoint = f'{REDDIT_BASE_URL}/r/{subreddit}/search'
    params = {
        'q': query,
        'limit': limit,
        'sort': sort,
    }
    headers = {
        'Authorization': f'bearer {token}',  
        'User-Agent': 'ChangeMeClient/0.1 by YourUsername'  
    }
    response = requests.get(endpoint, params=params, headers=headers)
    response.raise_for_status()
    return response.json()



def reddit_access_token(grant_type, username, password, client_id, client_secret):
    url = "https://www.reddit.com/api/v1/access_token"
    headers = {
        "User-Agent": "PostmanRuntime/7.39.0"  
    }
    data = {
        "grant_type": grant_type,
        "username": username,
        "password": password
    }
    auth = HTTPBasicAuth(client_id, client_secret)
    response = requests.post(url, data=data, headers=headers, auth=auth)
    response.raise_for_status()
    return response.json()