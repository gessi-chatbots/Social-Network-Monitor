import requests
from datetime import datetime
from bs4 import BeautifulSoup
from snmapp.models import Document
from snmapp.interfaces.service_interface import ServiceInterface
import uuid
from django.utils import timezone
from django.db import IntegrityError

class MastodonService(ServiceInterface):
    def search_posts(self, query, limit, token, from_date=None, to_date=None):
        endpoint = f'https://mastodon.social/api/v2/search'
        params = {'q': query, 'type': 'statuses', 'limit': limit}
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()
        return response.json().get('statuses', [])

    def filter_posts(self, posts, from_date=None, to_date=None):
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

    def save_posts(self, posts):
        saved_count = 0
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
                additionalType='mastodon'
            )
            try:
                document.save()
                saved_count += 1
            except IntegrityError:
                continue
        return saved_count
