from django.http import JsonResponse
from rest_framework import viewsets
from snmapp.models import Document
from snmapp.api.serializer import DocumentSerializer
from snmapp.services.mastodon_service import mastodon_query_search as mastodon_query_search
from snmapp.services.reddit_service import reddit_search as reddit_search, reddit_access_token as reddit_access_token
from snmapp.services.newsapi_service import newsapi_search as newsapi_search
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
from django.utils import timezone
from django.db import IntegrityError
from datetime import datetime
from bs4 import BeautifulSoup


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class SearchPostsView(APIView):
    def get(self, request, *args, **kwargs):
        platform = request.GET.get('platform')
        query = request.GET.get('q')
        limit = int(request.GET.get('limit', 10))
        token = request.GET.get('token')
        from_date = request.GET.get('from')
        to_date = request.GET.get('to')

        if platform not in ['mastodon', 'reddit', 'newsapi', 'local']:
            return Response({'error': 'Invalid platform provided'}, status=400)

        if platform == 'local':
            return self.search_local(query, limit, from_date, to_date)

        posts = []
        if platform == 'mastodon':
            og_limit = limit
            max_limit = 40
            if query:
                if not token:
                    return Response({'error': 'Mastodon token is required'}, status=400)
                try:
                    posts = mastodon_query_search(query, limit, token)
                except Exception as e:
                    return Response({'error': str(e)}, status=500)
            else:
                return Response({'error': 'No query provided'}, status=400)

            filtered_posts = self.filter_posts(posts.get('statuses', []), from_date, to_date)

            self.save_posts(filtered_posts, query)
            if og_limit > max_limit:
                limit = max_limit
                return Response({
                    'message': f'Mastodon only supports a maximum of {max_limit} results. Returning {limit} results.',
                    'posts': filtered_posts
                }, status=200)
            else:
                return Response(filtered_posts, status=200)

        elif platform == 'reddit':
            if not query:
                return Response({'error': 'No query provided for Reddit search'}, status=400)
            if not token:
                return Response({'error': 'Reddit token is required'}, status=400)
            subreddit = 'all'
            sort = request.GET.get('sort', '')
            try:
                posts = reddit_search(query, subreddit, limit, sort, token)
            except Exception as e:
                return Response({'error': str(e)}, status=500)

            children = [post.get('data') for post in posts.get('data', {}).get('children', [])]

            filtered_posts = self.filter_posts(children, from_date, to_date)
            filtered_posts = filtered_posts[:limit]

            self.save_posts(filtered_posts, query)
            return Response(filtered_posts, status=200)

        elif platform == 'newsapi':
            if not query:
                return Response({'error': 'No query provided for NewsAPI search'}, status=400)
            if not token:
                return Response({'error': 'NewsAPI token is required'}, status=400)

            apiKey = token
            pageSize = limit

            try:
                posts = newsapi_search(apiKey, query, from_date, to_date, pageSize)
            except Exception as e:
                return Response({'error': str(e)}, status=500)

            self.save_posts(posts['articles'], query)
            return Response(posts['articles'], status=200)

        return Response({'error': 'Invalid platform provided'}, status=400)

    def filter_posts(self, posts, from_date=None, to_date=None):
        filtered_posts = []
        platform = self.request.GET.get('platform')

        if platform == 'mastodon':

            if from_date:
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            if to_date:
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date and to_date:
                for post in posts:
                    try:
                        published_date = datetime.strptime(post["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ').date()
                        if from_date <= published_date <= to_date:
                            filtered_posts.append(post)
                    except (KeyError, ValueError) as e:
                        continue  
            elif from_date:
                for post in posts:
                    try:
                        published_date = datetime.strptime(post["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ').date()
                        if from_date <= published_date:
                            filtered_posts.append(post)
                    except (KeyError, ValueError) as e:
                        continue
            elif to_date:
                for post in posts:
                    try:
                        published_date = datetime.strptime(post["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ').date()
                        if published_date <= to_date:
                            filtered_posts.append(post)
                    except (KeyError, ValueError) as e:
                        continue
            else:
                filtered_posts = posts
                
        elif platform == 'reddit':
            if from_date:
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            if to_date:
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date and to_date:
                for post in posts:
                    try:
                        published_date = datetime.fromtimestamp(post["created"]).date()
                        if from_date <= published_date <= to_date:
                            filtered_posts.append(post)
                    except (KeyError, ValueError) as e:
                        continue
            elif from_date:
                for post in posts:
                    try:
                        published_date = datetime.fromtimestamp(post["created"]).date()
                        if from_date <= published_date:
                            filtered_posts.append(post)
                    except (KeyError, ValueError) as e:
                        continue
            elif to_date:
                for post in posts:
                    try:
                        published_date = datetime.fromtimestamp(post["created"]).date()
                        if published_date <= to_date:
                            filtered_posts.append(post)
                    except (KeyError, ValueError) as e:
                        continue
            else:
                filtered_posts = posts

        return filtered_posts

    def save_posts(self, posts, additional_type):
        platform = self.request.GET.get('platform')

        if platform == 'mastodon':
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

        elif platform == 'reddit':
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
                except IntegrityError:
                    continue

        elif platform == 'newsapi':
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
                

    def search_local(self, query, limit, from_date=None, to_date=None):
        filters = {}

        if query:
            filters['text__icontains'] = query
        if from_date:
            filters['datePublished__gte'] = from_date
        if to_date:
            filters['datePublished__lte'] = to_date

        documents = Document.objects.filter(**filters)[:limit]
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=200)


class RedditAccessTokenView(APIView):
    def post(self, request):
        grant_type = request.data.get('grant_type')
        username = request.data.get('username')
        password = request.data.get('password')
        client_id = request.data.get('client_id')
        client_secret = request.data.get('client_secret')

        if not (grant_type and username and password and client_id and client_secret):
            return Response({'error': 'Missing grant_type, username, password, client_id, or client_secret'}, status=400)

        try:
            access_token = reddit_access_token(grant_type, username, password, client_id, client_secret)
            return Response({'access_token': access_token}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class AddDocumentFromJSONView(APIView):
    def post(self, request, *args, **kwargs):
        platform = request.GET.get('platform')
        if platform not in ['mastodon', 'reddit', 'newsapi']:
            return Response({'error': 'Invalid platform provided. Only Mastodon, Reddit, and NewsAPI are supported for this endpoint.'}, status=400)

        data = request.data
        if not data:
            return Response({'error': 'No data provided in the request body.'}, status=400)

        saved_count = 0

        if platform == 'mastodon' or platform == 'reddit' or platform == 'newsapi':
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

                    elif platform == 'reddit':
                        if 'data' in entry:
                            children = entry['data'].get('children', [])
                            if children is not None:
                                for child in children:
                                    post = child.get('data', {})
                                    document = Document(
                                        identifier=str(uuid.uuid4()),
                                        text=post.get('selftext', ''),
                                        datePublished=datetime.utcfromtimestamp(post.get('created_utc')).strftime('%Y-%m-%d'),
                                        dateCreated=timezone.now().date(),
                                        author=post.get('author', 'Unknown'),
                                        url=f"https://www.reddit.com{post.get('permalink', '')}",
                                        alternateName=post.get('id', ''),
                                        additionalType='reddit'
                                    )
                                    document.save()
                                    saved_count += 1
                            else:
                                post = entry['data']
                                document = Document(
                                    identifier=str(uuid.uuid4()),
                                    text=post.get('selftext', ''),
                                    datePublished=datetime.utcfromtimestamp(post.get('created_utc')).strftime('%Y-%m-%d'),
                                    dateCreated=timezone.now().date(),
                                    author=post.get('author', 'Unknown'),
                                    url=f"https://www.reddit.com{post.get('permalink', '')}",
                                    alternateName=post.get('id', ''),
                                    additionalType='reddit'
                                )
                                document.save()
                                saved_count += 1
                                
                        else:
                            post = entry.get('data', {})
                            document = Document(
                                identifier=str(uuid.uuid4()),
                                text=post.get('selftext', ''),
                                datePublished=datetime.utcfromtimestamp(post.get('created_utc')).strftime('%Y-%m-%d'),
                                dateCreated=timezone.now().date(),
                                author=post.get('author', 'Unknown'),
                                url=f"https://www.reddit.com{post.get('permalink', '')}",
                                alternateName=post.get('id', ''),
                                additionalType='reddit'
                            )
                            document.save()
                            saved_count += 1

                    elif platform == 'newsapi':
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
                        else:
                            document = Document(
                                identifier=str(uuid.uuid4()),
                                text=entry.get('content', ''),
                                datePublished=entry.get('publishedAt', '').split('T')[0],
                                dateCreated=timezone.now().date(),
                                author=entry.get('author', 'Unknown'),
                                url=entry.get('url', ''),
                                alternateName=entry.get('source', {}).get('name', 'Unknown'),
                                additionalType='newsapi'
                            )
                            document.save()
                            saved_count += 1

                except Exception as e:
                    continue

        if saved_count > 0:
            return Response({'message': f'Successfully saved {saved_count} posts.'}, status=201)
        else:
            return Response({'error': 'No posts were saved.'}, status=400)

class AddDocumentFromParamsView(APIView):
    def post(self, request, *args, **kwargs):
        text = request.POST.get('text')
        author = request.POST.get('author')
        datePublished = request.POST.get('datePublished')

        if not all([text, author, datePublished]):
            return Response({'error': 'Text, Author and Date Published are required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            document = Document(
                identifier=str(uuid.uuid4()),
                text=text,
                datePublished=datePublished,  
                dateCreated=timezone.now().date(),
                author=author,
                url=request.POST.get('url', ''),
                alternateName=request.POST.get('alternateName', ''),
                additionalType=request.POST.get('additionalType', '')
            )
            document.save()
            return Response({'message': 'Document saved successfully.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentDetailView(APIView):
    def get(self, request, identifier, *args, **kwargs):
        try:
            document = Document.objects.get(identifier=identifier)
            serializer = DocumentSerializer(document)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Document.DoesNotExist:
            return Response({'error': f'Document with identifier: {identifier} not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, identifier, *args, **kwargs):
        try:
            document = Document.objects.get(identifier=identifier)
            updated_data = request.data
            allowed_fields = ['text', 'datePublished', 'url', 'author', 'alternateName', 'additionalType']
            for field in allowed_fields:
                if field in updated_data:
                    setattr(document, field, updated_data[field])
            document.save()
            return Response({'message': f'Document with identifier: {identifier} updated successfully.'}, status=status.HTTP_200_OK)
        except Document.DoesNotExist:
            return Response({'error': f'Document with identifier: {identifier} not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, identifier, *args, **kwargs):
        try:
            document = Document.objects.get(identifier=identifier)
            document.delete()
            return Response({'message': f'Document with identifier: {identifier} deleted successfully.'}, status=status.HTTP_200_OK)
        except Document.DoesNotExist:
            return Response({'error': f'Document with identifier: {identifier} not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)