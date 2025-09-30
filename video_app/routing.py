"""
WebSocket URL routing for the video_app
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/gesture-session/(?P<session_id>[0-9a-f-]+)/$', consumers.GestureConsumer.as_asgi()),
    re_path(r'ws/gesture-stream/$', consumers.GestureStreamConsumer.as_asgi()),
]
