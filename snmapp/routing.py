from django.urls import path
from snmapp.consumers import MastodonConsumer

websocket_urlpatterns = [
    path('ws/mastodon/<str:query>/<str:token>/', MastodonConsumer.as_asgi()),
]
