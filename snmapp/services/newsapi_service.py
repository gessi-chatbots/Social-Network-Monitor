import requests
from datetime import datetime
from snmapp.models import Document
import uuid
from django.db import IntegrityError
from django.utils import timezone

NEWSAPI_BASE_URL = 'https://newsapi.org/v2/everything'

def newsapi_query_search(apiKey, q, from_date='', to_date='', pageSize=''):
    params = {
        'apiKey': apiKey,
        'q': q,
        'from': from_date,
        'to': to_date,
        'pageSize': pageSize
    }
    
    params = {key: value for key, value in params.items() if value}
    headers = {}
    response = requests.get(NEWSAPI_BASE_URL, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

def search_newsapi_posts(apiKey, query, limit, from_date=None, to_date=None):
    if not query:
        raise ValueError('No query provided for NewsAPI search')
    if not apiKey:
        raise ValueError('NewsAPI token is required')

    posts = newsapi_query_search(apiKey, query, from_date, to_date, limit)
    filtered_posts = filter_newsapi_posts(posts.get('articles', []), from_date, to_date)
    save_newsapi_posts(filtered_posts, query)
    return filtered_posts

def filter_newsapi_posts(posts, from_date=None, to_date=None):
    filtered_posts = []

    if from_date:
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    if to_date:
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

    for post in posts:
        try:
            published_date = datetime.strptime(post.get('publishedAt', ''), '%Y-%m-%dT%H:%M:%SZ').date()
            if (not from_date or from_date <= published_date) and (not to_date or published_date <= to_date):
                filtered_posts.append(post)
        except (KeyError, ValueError):
            continue

    return filtered_posts

def save_newsapi_posts(posts, additional_type):
    for post in posts:
        author = post.get('author', 'Unknown')
        if author is None or author.startswith('https'):
            author = post.get('source', {}).get('name', 'Unknown')

        document = Document(
            identifier=str(uuid.uuid4()),
            text=post.get('content', ''),
            datePublished=datetime.strptime(post.get('publishedAt', ''), '%Y-%m-%dT%H:%M:%SZ').date(),
            dateCreated=timezone.now().date(),
            author=author,
            url=post.get('url', ''),
            alternateName=post.get('title', ''),
            additionalType=additional_type
        )
        try:
            document.save()
        except IntegrityError:
            continue

def save_articles_json_newsapi(data):
    saved_count = 0
    entries = []

    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        entries = [data]

    for entry in entries:
        try:
            if 'articles' in entry:
                articles = entry['articles']
                for article in articles:
                    document = Document(
                        identifier=str(uuid.uuid4()),
                        text=article.get('content', ''),
                        datePublished=article.get('publishedAt', '').split('T')[0],
                        dateCreated=timezone.now().date(),
                        author=article.get('author', 'Unknown'),
                        url=article.get('url', ''),
                        alternateName=article.get('source', {}).get('name', 'Unknown'),
                        additionalType='newsapi'
                    )
                    document.save()
                    saved_count += 1

        except Exception as e:
            continue

    return saved_count