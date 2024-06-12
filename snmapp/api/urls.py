from rest_framework.routers import DefaultRouter
from snmapp.api.views import DocumentViewSet, SearchPostsView, RedditAccessTokenView, DocumentDetailView, AddDocumentFromJSONView, AddDocumentFromParamsView
from django.urls import path

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('posts/', SearchPostsView.as_view(), name='search_posts'),
    path('reddit_token', RedditAccessTokenView.as_view(), name='reddit_token'),
    path('add_by_json/', AddDocumentFromJSONView.as_view(), name='add_post_json'),
    path('add_by_params', AddDocumentFromParamsView.as_view(), name='add_post_params'),
    path('post/<str:identifier>', DocumentDetailView.as_view(), name='document_detail'), 

]

urlpatterns += router.urls
