from django.http import JsonResponse
from rest_framework import viewsets
from snmapp.models import Document
from snmapp.api.serializer import DocumentSerializer
from snmapp.services.mastodon_service import mastodon_hashtag_search as mastodon_hashtag_search, mastodon_query_search as mastodon_query_search
from snmapp.services.reddit_service import reddit_search as reddit_search, reddit_access_token as reddit_access_token
from snmapp.services.newsapi_service import newsapi_search as newsapi_search
from rest_framework.views import APIView
from rest_framework.response import Response
import uuid
from django.utils import timezone
from django.db import IntegrityError
from datetime import datetime 




class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class SearchPostsView(APIView):
    def get(self, request, *args, **kwargs):
        platform = request.GET.get('platform')
        hashtag = request.GET.get('hashtag')
        query = request.GET.get('q')    
        content_type = request.GET.get('type')
        limit = int(request.GET.get('limit', 10))  # Conversión a entero aquí
        token = request.GET.get('token')

        if platform not in ['mastodon', 'reddit', 'newsapi', 'local']:
            return Response({'error': 'Invalid platform provided'}, status=400)
        
        if platform == 'local':
            return self.search_local(query, hashtag, content_type, limit)

        posts = []
        if platform == 'mastodon':
            if hashtag:
                try:
                    posts = mastodon_hashtag_search(hashtag, limit)
                except Exception as e:
                    return Response({'error': str(e)}, status=500)
            elif query:
                if query is None:
                    return Response({'error': 'Query parameter is required for query search action'}, status=400)
                elif not token:
                    return Response({'error': 'Mastodon token is required'}, status=400)
                try:
                    posts = mastodon_query_search(query, content_type, limit, token)
                except Exception as e:
                    return Response({'error': str(e)}, status=500)
            else:
                return Response({'error': 'No hashtag or query provided'}, status=400)

            self.save_posts(posts, query if query else hashtag)
            return Response(posts, status=200)

        elif platform == 'reddit':
            if not query:
                return Response({'error': 'No query provided for Reddit search'}, status=400)
            if not token:
                return Response({'error': 'Reddit token is required'}, status=400)
            subreddit = 'all'
            category = request.GET.get('category', '')
            count = request.GET.get('count', '')
            sort = request.GET.get('sort', '')
            t = request.GET.get('t', '')
            type = request.GET.get('type', '')

            try:
                posts = reddit_search(query, subreddit, category, count, limit, sort, t, type, token)
            except Exception as e:
                return Response({'error': str(e)}, status=500)
            
            self.save_posts(posts, query)
            return Response(posts, status=200)
        
        elif platform == 'newsapi':
            if not query:
                return Response({'error': 'No query provided for NewsAPI search'}, status=400)
            if not token:
                return Response({'error': 'NewsAPI token is required'}, status=400)

            # Parámetros adicionales de NewsAPI
            searchIn = request.GET.get('searchIn')
            sources = request.GET.get('sources')
            domains = request.GET.get('domains')
            excludeDomains = request.GET.get('excludeDomains')
            from_date = request.GET.get('from')
            to_date = request.GET.get('to')
            language = request.GET.get('language', '')
            #sortBy = request.GET.get('sort', '')
            apiKey = token
            page = request.GET.get('page', '')
            pageSize = request.GET.get('pageSize', '')

            try:
                posts = newsapi_search(apiKey, query, searchIn, sources, domains, excludeDomains, from_date, to_date, language, page, pageSize)
            except Exception as e:
                return Response({'error': str(e)}, status=500)

            self.save_posts(posts, query)
            return Response(posts, status=200)
        
        return Response({'error': 'Invalid platform provided'}, status=400)
    
    
    
    def save_posts(self, posts, additional_type):
        platform = self.request.GET.get('platform')
        
        if platform == 'mastodon':
            for post in posts.get('statuses', []):  # Suponiendo que los resultados de Mastodon están en 'statuses'
                document = Document(
                    identifier=str(uuid.uuid4()),
                    text=post.get('content', ''),
                    datePublished=post.get('created_at', '').split('T')[0],  # Asegúrate de que el formato de fecha sea correcto
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
            for post in posts.get('data', {}).get('children', []):
                data = post.get('data', {})
                date_published = datetime.fromtimestamp(data.get('created', ''))
                document = Document(
                    identifier=str(uuid.uuid4()),
                    text=data.get('selftext', ''),
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
            for post in posts.get('articles', []):
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
                
        
            
    def search_local(self, query, hashtag, content_type, limit):
        filters = {}
        if query:
            filters['text__icontains'] = query
        if hashtag:
            filters['additionalType__icontains'] = hashtag

        documents = Document.objects.filter(**filters)[:limit]
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=200)
    

class RedditAccessTokenView(APIView):
    def post(self, request):
        grant_type = request.data.get('grant_type')
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not (grant_type and username and password):
            return Response({'error': 'Missing grant_type, username, or password'}, status=400)
        
        try:
            access_token = reddit_access_token(grant_type, username, password)
            return Response({'access_token': access_token}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

        
    
    
