from django.http import JsonResponse
from rest_framework import viewsets
from app.models import Document
from app.api.serializer import DocumentSerializer
from app.services.mastodon_service import mastodon_hashtag_search as mastodon_hashtag_search, mastodon_query_search as mastodon_query_search
"""from app.services.reddit_service import fetch_posts_by_hashtag as fetch_reddit_posts_by_hashtag, search_posts as search_reddit_posts"""
from rest_framework.views import APIView
from rest_framework.response import Response

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class SearchPostsView(APIView):
    def get(self, request, *args, **kwargs):
        platform = request.GET.get('platform')
        hashtag = request.GET.get('hashtag')
        query = request.GET.get('q')
        content_type = request.GET.get('type')
        limit = request.GET.get('limit', 10) 
        mastodon_token = request.GET.get('mastodon_token')  # Obtener el token de acceso de Mastodon


        if platform not in ['mastodon', 'reddit', 'newsapi']:
            return Response({'error': 'Invalid platform provided'}, status=400)

        if platform == 'mastodon':
            if hashtag:
                try:
                    posts = mastodon_hashtag_search(hashtag, limit)
                    return Response(posts, status=200)
                except Exception as e:
                    return Response({'error': str(e)}, status=500)
            elif query:
                if query is None:
                    return Response({'error': 'Query parameter is required for query search action'}, status=400)
                elif not mastodon_token:
                    return Response({'error': 'Mastodon token is required'}, status=400)
                try:
                    posts = mastodon_query_search(query, content_type, limit, mastodon_token)
                    return Response(posts, status=200)
                except Exception as e:
                    return Response({'error': str(e)}, status=500)
            else:
                return Response({'error': 'No hashtag or query provided'}, status=400)
        
        """ elif platform == 'reddit':
            if hashtag:
                try:
                    posts = fetch_reddit_posts_by_hashtag(hashtag, limit)
                    return Response(posts, status=200)
                except Exception as e:
                    return Response({'error': str(e)}, status=500)
            elif query:
                if content_type is None:
                    return Response({'error': 'Content type parameter is required for query action'}, status=400)
                try:
                    posts = search_reddit_posts(query, content_type, limit)
                    return Response(posts, status=200)
                except Exception as e:
                    return Response({'error': str(e)}, status=500)
            else:
                return Response({'error': 'No hashtag or query provided'}, status=400) """
