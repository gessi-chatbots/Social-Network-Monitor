import requests
import uuid
from bs4 import BeautifulSoup
from datetime import datetime
from django.db import IntegrityError
from django.utils import timezone
from mastodon import Mastodon
from snmapp.models import Document


MASTODON_BASE_URL_V2 = 'https://mastodon.social/api/v2'


def mastodon_query_search(query, limit=10, token=None):
    endpoint = f'{MASTODON_BASE_URL_V2}/search'
    params = {'q': query, 'type': 'statuses', 'limit': limit}
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(endpoint, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

def search_mastodon_posts(query, limit, token, from_date=None, to_date=None):
    if not query:
        raise ValueError('No query provided for Mastodon search')
    if not token:
        raise ValueError('Mastodon token is required')

    posts = mastodon_query_search(query, limit, token)
    filtered_posts = filter_mastodon_posts(posts.get('statuses', []), from_date, to_date)
    save_mastodon_posts(filtered_posts, query)
    return filtered_posts

def filter_mastodon_posts(posts, from_date=None, to_date=None):
    filtered_posts = []

    if from_date:
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    if to_date:
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

    for post in posts:
        try:
            published_date = datetime.strptime(post["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ').date()
            if (not from_date or from_date <= published_date) and (not to_date or published_date <= to_date):
                filtered_posts.append(post)
        except (KeyError, ValueError):
            continue

    return filtered_posts

def save_mastodon_posts(posts, additional_type):
    for post in posts:
        html_content = post.get('content', '')
        content = BeautifulSoup(html_content, 'html.parser').get_text()
        
        document = Document(
            identifier=str(uuid.uuid4()),
            text=content,
            datePublished=post.get('created_at', '').split('T')[0],
            dateCreated=timezone.now().date(),
            author=post.get('account', {}).get('username', 'Unknown'),
            url=post.get('url', ''),
            alternateName=post.get('id', ''),
            additionalType=additional_type
        )
        try:
            document.save()
        except IntegrityError:
            continue

def save_posts_json_mastodon(data, platform):
    saved_count = 0
    entries = []

    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        entries = [data]

    for entry in entries:
        try:
            if platform == 'mastodon':
                if 'statuses' in entry:
                    statuses = entry['statuses']
                    for post in statuses:
                        html_content = post.get('content', '')
                        content = BeautifulSoup(html_content, 'html.parser').get_text()
                        document = Document(
                            identifier=str(uuid.uuid4()),
                            text=content,
                            datePublished=post.get('created_at', '').split('T')[0],
                            dateCreated=timezone.now().date(),
                            author=post.get('account', {}).get('username', 'Unknown'),
                            url=post.get('url', ''),
                            alternateName=post.get('id', ''),
                            additionalType='mastodon'
                        )
                        document.save()
                        saved_count += 1
                else:
                    html_content = entry.get('content', '')
                    content = BeautifulSoup(html_content, 'html.parser').get_text()
                    document = Document(
                        identifier=str(uuid.uuid4()),
                        text=entry.get('content', ''),
                        datePublished=entry.get('created_at', '').split('T')[0],
                        dateCreated=timezone.now().date(),
                        author=entry.get('account', {}).get('username', 'Unknown'),
                        url=entry.get('url', ''),
                        alternateName=entry.get('id', ''),
                        additionalType='mastodon'
                    )
                    document.save()
                    saved_count += 1

        except Exception as e:
            continue

    return saved_count

def mastodon_async_search(query, limit, token):
    mastodon = Mastodon(access_token=token, api_base_url='https://mastodon.social')
    return mastodon.search_v2(q=query, limit=limit, resolve=True)