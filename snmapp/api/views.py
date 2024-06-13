from django.http import JsonResponse
from rest_framework import viewsets
from snmapp.models import Document
from snmapp.api.serializer import DocumentSerializer
from snmapp.services.mastodon_service import mastodon_query_search, filter_mastodon_posts, save_mastodon_posts, save_posts_json_mastodon, search_mastodon_posts
from snmapp.services.reddit_service import reddit_query_search, reddit_access_token, filter_reddit_posts, save_reddit_posts, save_posts_json_reddit, search_reddit_posts
from snmapp.services.newsapi_service import newsapi_query_search, filter_newsapi_posts, save_newsapi_posts, save_articles_json_newsapi, search_newsapi_posts
from snmapp.services.local_service import get_document, update_document, delete_document, save_document_from_params
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
            return Response({'error': 'Invalid platform provided'}, status=status.HTTP_400_BAD_REQUEST)
        if not query:
            return Response({'error': 'No query provided'}, status=status.HTTP_400_BAD_REQUEST)
        if platform != 'local' and not token:
            return Response({'error': f'Token is required for {platform.capitalize()} search'}, status=status.HTTP_400_BAD_REQUEST)


        if platform == 'local':
            return self.search_local(query, limit, from_date, to_date)
        elif platform == 'mastodon':
            filtered_posts = search_mastodon_posts(query, limit, token, from_date, to_date)
        elif platform == 'reddit':
            filtered_posts = search_reddit_posts(query, limit, token, from_date, to_date)
        elif platform == 'newsapi':
            filtered_posts = search_newsapi_posts(query, limit, token, from_date, to_date)
        else:
            return Response({'error': 'Invalid platform provided'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(filtered_posts, status=status.HTTP_200_OK)
    
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

        try:
            saved_count = 0

            if platform == 'mastodon':
                saved_count = save_posts_json_mastodon(data)
            elif platform == 'reddit':
                saved_count = save_posts_json_reddit(data)
            elif platform == 'newsapi':
                saved_count = save_articles_json_newsapi(data)

            if saved_count > 0:
                return Response({'message': f'Successfully saved {saved_count} posts.'}, status=201)
            else:
                return Response({'error': 'No posts were saved.'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
        
class AddDocumentFromParamsView(APIView):
    def post(self, request, *args, **kwargs):
        text = request.POST.get('text')
        author = request.POST.get('author')
        date_published = request.POST.get('datePublished')

        if not all([text, author, date_published]):
            return Response({'error': 'Text, Author and Date Published are required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        url = request.POST.get('url', '')
        alternate_name = request.POST.get('alternateName', '')
        additional_type = request.POST.get('additionalType', '')

        success, message = save_document_from_params(text, author, date_published, url, alternate_name, additional_type)

        if success:
            return Response({'message': message}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentDetailView(APIView):
    def get(self, request, identifier, *args, **kwargs):
        try:
            document = get_document(identifier)
            serializer = DocumentSerializer(document)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, identifier, *args, **kwargs):
        try:
            updated_data = request.data
            update_document(identifier, updated_data)
            return Response({'message': f'Document with identifier: {identifier} updated successfully.'}, status=status.HTTP_200_OK)
        except Document.DoesNotExist:
            return Response({'error': f'Document with identifier: {identifier} not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, identifier, *args, **kwargs):
        try:
            delete_document(identifier)
            return Response({'message': f'Document with identifier: {identifier} deleted successfully.'}, status=status.HTTP_200_OK)
        except Document.DoesNotExist:
            return Response({'error': f'Document with identifier: {identifier} not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)