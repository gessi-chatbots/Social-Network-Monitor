import requests
import uuid
from bs4 import BeautifulSoup
from datetime import datetime
from django.db import IntegrityError
from django.utils import timezone
from mastodon import Mastodon
from snmapp.models import Document
from snmapp.interfaces.service_interface import ServiceInterface
import logging
import re

logger = logging.getLogger(__name__)


class MastodonService(ServiceInterface):
    def search_posts(self, query, limit, token, from_date=None, to_date=None):
        try:
            endpoint = f'https://mastodon.social/api/v2/search'
            if limit is None:
                params = {'q': query, 'type': 'statuses'}
            else:
                params = {'q': query, 'type': 'statuses', 'limit': limit}
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(endpoint, params=params, headers=headers)
            response.raise_for_status()
            return response.json().get('statuses', [])
        except requests.RequestException as e:
            logger.error(f"Failed to fetch posts from Mastodon: {e}")
            raise

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

    def save_posts(self, posts, additional_type, plataform_name, category):
        saved_count = 0

        for post in posts:
            html_content = post.get('content', '')
            content = BeautifulSoup(html_content, 'html.parser').get_text()

            content = self.clean_content(content)

            document = Document(
                identifier=str(uuid.uuid4()),
                text=content,
                datePublished=post.get('created_at', '').split('T')[0],
                dateCreated=timezone.now().date(),
                author=post.get('account', {}).get('username', 'Unknown'),
                url=post.get('url', ''),
                alternateName=post.get('id', ''),
                additionalType=additional_type,
                plataformName=plataform_name,
                categoryType=category
            )
            try:
                document.save()
                saved_count += 1
            except IntegrityError:
                continue

        return saved_count

    def clean_content(self, content):
        return re.sub(r'[^\x00-\x7F]+', '', content)

    def save_posts_json(self, data):
        saved_count = 0
        entries = []

        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            entries = [data]

        for entry in entries:
            try:
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

    def reddit_access_token(self, grant_type, username, password, client_id, client_secret):
        pass
