import requests
from datetime import datetime
from snmapp.models import Document
import uuid
from django.db import IntegrityError
from django.utils import timezone
import logging
from snmapp.interfaces.service_interface import ServiceInterface


logger = logging.getLogger(__name__)

class NewsAPIService(ServiceInterface):
    def search_posts(self, query, limit, token, from_date=None, to_date=None):
        try:
            endpoint = f'https://newsapi.org/v2/everything'
            params = {
                'apiKey': token,
                'q': query,
                'from': from_date,
                'to': to_date,
                'pageSize': limit
            }
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json().get('articles', [])
        except requests.RequestException as e:
            logger.error(f"Failed to fetch posts from NewsAPI: {e}")
            raise

    def filter_posts(self, posts, from_date=None, to_date=None):
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

    def save_posts(self, posts, additional_type):
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

    def save_posts_json(self, data):
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