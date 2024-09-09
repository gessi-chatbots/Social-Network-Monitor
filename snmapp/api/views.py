from django.http import JsonResponse
from rest_framework import viewsets
from snmapp.models import Document
from snmapp.api.serializer import DocumentSerializer
from snmapp.services.mastodon_service import MastodonService
from snmapp.services.reddit_service import RedditService
from snmapp.services.newsapi_service import NewsAPIService
from snmapp.services.local_service import get_document, update_document, delete_document, save_document_from_params, search_local
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests



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

        try:
            if platform == 'local':
                return search_local(query, limit, from_date, to_date)
            elif platform == 'mastodon':
                service = MastodonService()
            elif platform == 'reddit':
                service = RedditService()
            elif platform == 'newsapi':
                service = NewsAPIService()

        except ValueError as ve:
            return JsonResponse({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.HTTPError as he:
            return JsonResponse({'error': str(he), 'details': he.response.text}, status=he.response.status_code)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            posts = service.search_posts(query, limit, token, from_date, to_date)
            # filtered_posts = service.filter_posts(posts, from_date, to_date)
            saved_count = service.save_posts(posts, query)
            
            if saved_count > 0:
                message = f"Number of saved posts: {saved_count}"
            else:
                message = f"No posts were saved"

            response = JsonResponse({'Message': message, 'Posts': posts}, status=status.HTTP_200_OK)
            return response
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            service = RedditService()
            access_token = service.reddit_access_token(grant_type, username, password, client_id, client_secret)
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
                service = MastodonService()
                saved_count = service.save_posts_json(data)
            elif platform == 'reddit':
                service = RedditService()
                saved_count = service.save_posts_json(data)
            elif platform == 'newsapi':
                service = NewsAPIService()
                saved_count = service.save_posts_json(data)

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