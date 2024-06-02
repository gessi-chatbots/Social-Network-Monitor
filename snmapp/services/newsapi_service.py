import requests

NEWSAPI_BASE_URL = 'https://newsapi.org/v2/everything'

def newsapi_search(apiKey, q, searchIn='', sources='', domains='', excludeDomains='', from_date='', to_date='', language='', page='', pageSize=''):
    params = {
        'apiKey': apiKey,
        'q': q,
        'searchIn': searchIn,
        'sources': sources,
        'domains': domains,
        'excludeDomains': excludeDomains,
        'from': from_date,
        'to': to_date,
        'language': language,
        #'sortBy': sortBy,
        'page': page,
        'pageSize': pageSize
    }
    
    params = {key: value for key, value in params.items() if value}
    headers = {}
    response = requests.get(NEWSAPI_BASE_URL, params=params, headers=headers)
    response.raise_for_status()
    return response.json()
