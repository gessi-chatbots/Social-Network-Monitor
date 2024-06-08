import requests

NEWSAPI_BASE_URL = 'https://newsapi.org/v2/everything'

def newsapi_search(apiKey, q, from_date='', to_date='', pageSize=''):
    params = {
        'apiKey': apiKey,
        'q': q,
        'from': from_date,
        'to': to_date,
        #'sortBy': sortBy,
        'pageSize': pageSize
    }
    
    params = {key: value for key, value in params.items() if value}
    headers = {}
    response = requests.get(NEWSAPI_BASE_URL, params=params, headers=headers)
    response.raise_for_status()
    return response.json()
