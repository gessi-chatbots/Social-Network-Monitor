import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from mastodon import Mastodon, StreamListener

class MastodonStreamListener(StreamListener):
    def __init__(self, send_func):
        super().__init__()
        self.send_func = send_func

    async def on_update(self, status):
        await self.send_func({
            'type': 'post',
            'content': status
        })

    async def on_abort(self, error):
        await self.send_func({
            'type': 'error',
            'content': str(error)
        })

class MastodonConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.query = self.scope['url_route']['kwargs']['query']
        self.token = self.scope['url_route']['kwargs']['token']
        await self.accept()

        # Start a task to fetch posts continuously
        self.listener_task = asyncio.create_task(self.fetch_posts())

    async def disconnect(self, close_code):
        self.listener_task.cancel()

    async def receive(self, text_data):
        pass

    async def fetch_posts(self):
        mastodon = Mastodon(access_token=self.token, api_base_url='https://mastodon.social')
        stream_listener = MastodonStreamListener(self.send_json_wrapper)

        try:
            await mastodon.stream_public(stream_listener, run_async=True)
        except Exception as e:
            await self.send_json({
                'type': 'error',
                'content': str(e)
            })

    async def send_json_wrapper(self, message):
        await self.send_json(message)
