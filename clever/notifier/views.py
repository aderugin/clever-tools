# -*- coding: utf-8 -*-

from .models import Notification
from django.views.generic.detail import BaseDetailView
from django.http import HttpResponse
from django.utils import simplejson


class JSONResponseMixin(object):
    def render_to_response(self, context):
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        return HttpResponse(content, content_type='application/json', **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        return simplejson.dumps(context)


class AjaxLoadVars(JSONResponseMixin, BaseDetailView):
    model = Notification

    def render_to_response(self, context):
        obj = context['object']

        variables = [
            {'DOMAIN': u'Домен'},
            {'SITE_NAME': u'Название сайта'},
            {'DEFAULT_EMAIL_FROM': u'email по умолчанию'},
            {'DEFAULT_SMS_FROM': u'sms отправитель по умолчанию'},
        ]

        for var in obj.variables.all():
            variables.append({var.code: var.name})

        return JSONResponseMixin.render_to_response(self, {'vars': variables})
