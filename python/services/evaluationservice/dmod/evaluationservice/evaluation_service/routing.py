#!/usr/bin/env python3
from django.conf.urls import url, re_path

from service.application_values import CHANNEL_NAME_PATTERN

from . import consumers

websocket_urlpatterns = [
    re_path(f'ws/channel/(?P<channel_name>{CHANNEL_NAME_PATTERN})/?', consumers.ChannelConsumer.as_asgi(), name="Channel")
]
