from rest_framework.routers import DefaultRouter
from snmapp.api.views import DocumentViewSet, SearchPostsView, RedditAccessTokenView, DeleteDocumentView, AddDocumentFromJSONView, AddDocumentFromParamsView, UpdateDocumentView
from django.urls import path

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('posts/', SearchPostsView.as_view(), name='search_posts'),
    path('reddit_token/', RedditAccessTokenView.as_view(), name='reddit_token'),
    path('posts/', DeleteDocumentView.as_view(), name='delete_posts'),
    path('add_by_json/', AddDocumentFromJSONView.as_view(), name='add_post_json'),
    path('add_by_params/', AddDocumentFromParamsView.as_view(), name='add_post_params'),
    path('post/', UpdateDocumentView.as_view(), name='update_post'),

]

urlpatterns += router.urls
