import requests
from mastodon import Mastodon


MASTODON_BASE_URL_V2 = 'https://mastodon.social/api/v2'


def mastodon_query_search(query, limit=10, token=None):
    endpoint = f'{MASTODON_BASE_URL_V2}/search'
    params = {'q': query, 'type': 'statuses', 'limit': limit}
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(endpoint, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def mastodon_async_search(query, limit, token):
    mastodon = Mastodon(access_token=token, api_base_url='https://mastodon.social')
    return mastodon.search_v2(q=query, limit=limit, resolve=True)