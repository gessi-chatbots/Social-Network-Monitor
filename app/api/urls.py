from rest_framework.routers import DefaultRouter
from app.api.views import DocumentViewSet, SearchPostsView
from django.urls import path, include

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('search_posts/', SearchPostsView.as_view(), name='search_posts'),
]

urlpatterns += router.urls
