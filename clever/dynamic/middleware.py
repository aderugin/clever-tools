# -*- coding: utf-8 -*-
from clever.dynamic.base import DynamicSettings


class RequestSettingMiddleware(object):
    def process_request(self, request):
        DynamicSettings.reload_settings()