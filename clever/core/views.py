# -*- coding: utf-8 -*-

from django.views.generic.base import View
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
import json


class AjaxMixin(View):
    '''
    Миксин, формирующий JSON ответ. Достаточно переопределить
    get_ajax_data и вернуть в нем словарь
    '''
    def get_ajax_data(self, **kwargs):
        return { }

    def get(self, request, *args, **kwargs):
        response = super(AjaxMixin, self).get(request, request, *args, **kwargs)
        if request.is_ajax():
            data = self.get_ajax_data(**kwargs)
            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), mimetype='application/json')
        else:
            return response