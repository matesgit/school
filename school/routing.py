# core/routing.py

from django.urls import re_path
from core import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.GroupChatConsumer.as_asgi()),
    re_path(
        r'ws/privatechat/(?P<sender_type>\w+)/(?P<sender_id>\d+)/(?P<receiver_type>\w+)/(?P<receiver_id>\d+)/$',
        consumers.PrivateChatConsumer.as_asgi()
    ),
 
    
]
