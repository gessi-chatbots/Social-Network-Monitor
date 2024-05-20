import requests


MASTODON_BASE_URL_V1 = 'https://mastodon.social/api/v1'

MASTODON_BASE_URL_V2 = 'https://mastodon.social/api/v2'

def mastodon_hashtag_search(hashtag, limit=10):
    endpoint = f'{MASTODON_BASE_URL_V1}/timelines/tag/{hashtag}'
    params = {'limit': limit}
    response = requests.get(endpoint, params=params)
    response.raise_for_status()  # Si hay un error en la solicitud, lanzar una excepción
    return response.json()

def mastodon_query_search(query, content_type='statuses', limit=10, token=None):
    endpoint = f'{MASTODON_BASE_URL_V2}/search'
    params = {'q': query, 'type': content_type, 'limit': limit}
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(endpoint, params=params, headers=headers)
    response.raise_for_status()
    return response.json()
