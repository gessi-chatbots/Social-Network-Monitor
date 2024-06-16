import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from snmapp.models import Document
import uuid
from django.db import IntegrityError
from django.utils import timezone
from snmapp.interfaces.service_interface import ServiceInterface
import logging

logger = logging.getLogger(__name__)


class RedditService(ServiceInterface):
    def search_posts(self, query, limit, token, from_date=None, to_date=None):
        try:
            endpoint = f'https://oauth.reddit.com/search.json'
            params = {'q': query, 'limit': limit}
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(endpoint, params=params, headers=headers)
            response.raise_for_status()
            posts = response.json()
            children = [post.get('data') for post in posts.get('data', {}).get('children', [])]
            return children
        except requests.RequestException as e:
            logger.error(f"Failed to fetch posts from Reddit: {e}")
            raise

    def reddit_access_token(self, grant_type, username, password, client_id, client_secret):
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

    def filter_posts(self, posts, from_date=None, to_date=None):
        filtered_posts = []

        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

        for post in posts:
            try:
                published_date = datetime.fromtimestamp(post["created"]).date()
                if (not from_date or from_date <= published_date) and (not to_date or published_date <= to_date):
                    filtered_posts.append(post)
            except (KeyError, ValueError):
                continue

        return filtered_posts

    def save_posts(self, posts, additional_type):
        saved_count = 0
        
        for post in posts:
            data = post
            date_published = datetime.fromtimestamp(data.get('created', ''))
            text = data.get('selftext', '')
            if not text:
                text = data.get('title', '')
            document = Document(
                identifier=str(uuid.uuid4()),
                text=text,
                datePublished=date_published,
                dateCreated=timezone.now().date(),
                author=data.get('author', 'Unknown'),
                url=f"https://www.reddit.com{data.get('permalink', '')}",
                alternateName=data.get('id', ''),
                additionalType=additional_type
            )
            try:
                document.save()
                saved_count += 1
            except IntegrityError:
                continue
            
        return saved_count
            
    def save_posts_json(self, data):
        saved_count = 0
        entries = []

        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            entries = [data]

        for entry in entries:
            try:
                if 'data' in entry:
                    children = entry['data'].get('children', [])
                    for child in children:
                        post = child.get('data', {})
                        text = post.get('selftext', '')
                        if not text:
                            text = post.get('title', '')
                        document = Document(
                            identifier=str(uuid.uuid4()),
                            text=text,
                            datePublished=datetime.utcfromtimestamp(post.get('created_utc')).strftime('%Y-%m-%d'),
                            dateCreated=timezone.now().date(),
                            author=post.get('author', 'Unknown'),
                            url=f"https://www.reddit.com{post.get('permalink', '')}",
                            alternateName=post.get('id', ''),
                            additionalType='reddit'
                        )
                        document.save()
                        saved_count += 1

            except Exception as e:
                continue

        return saved_count
            