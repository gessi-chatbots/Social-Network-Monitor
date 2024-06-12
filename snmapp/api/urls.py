from rest_framework.routers import DefaultRouter
from snmapp.api.views import DocumentViewSet, SearchPostsView, RedditAccessTokenView, DeleteDocumentView, AddDocumentFromJSONView, AddDocumentFromParamsView, UpdateDocumentView, GetDocumentView
from django.urls import path

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('posts', SearchPostsView.as_view(), name='search_posts'),
    path('reddit_token', RedditAccessTokenView.as_view(), name='reddit_token'),
    path('post/<str:identifier>', DeleteDocumentView.as_view(), name='delete_post'), 
    path('add_by_json', AddDocumentFromJSONView.as_view(), name='add_post_json'),
    path('add_by_params', AddDocumentFromParamsView.as_view(), name='add_post_params'),
    path('post/<str:identifier>', UpdateDocumentView.as_view(), name='update_post'),
    path('post/<str:identifier>', GetDocumentView.as_view(), name='get_post'),  
]

urlpatterns += router.urls
