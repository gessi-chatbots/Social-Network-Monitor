from rest_framework.routers import DefaultRouter
from snmapp.api.views import DocumentViewSet, SearchPostsView, RedditAccessTokenView
from django.urls import path

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('search_posts/', SearchPostsView.as_view(), name='search_posts'),
    path('reddit_token/', RedditAccessTokenView.as_view(), name='reddit_token'),
]

urlpatterns += router.urls
