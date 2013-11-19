# -*- coding: utf-8 -*-

from django.views.generic.base import View
from django.views.generic.list import ListView
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.http import HttpResponseNotFound
import json


#-------------------------------------------------------------------------------
class AjaxDataMixin(object):
    def get_ajax_data(self, **kwargs):
        return {}


#-------------------------------------------------------------------------------
class AjaxMixin(View, AjaxDataMixin):
    '''
    Миксин, формирующий JSON ответ для GET запроса. Достаточно переопределить
    get_ajax_data и вернуть в нем словарь
    '''

    def get(self, request, *args, **kwargs):
        response = super(AjaxMixin, self).get(request, request, *args, **kwargs)
        if request.is_ajax():
            data = self.get_ajax_data(**kwargs)
            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), mimetype='application/json')
        else:
            return response


#-------------------------------------------------------------------------------
class AjaxListMixin(ListView, AjaxDataMixin):
    '''
    Миксин, формирующий JSON ответ для GET запроса. Достаточно переопределить
    get_ajax_data и вернуть в нем словарь
    '''

    def get(self, request, *args, **kwargs):
        response = super(AjaxListMixin, self).get(request, request, *args, **kwargs)
        if request.is_ajax():
            data = self.get_ajax_data(object_list=self.object_list, **kwargs)
            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), mimetype='application/json')
        else:
            return response


#-------------------------------------------------------------------------------
class AjaxProcessMixin(View, AjaxDataMixin):
    '''
    Миксин, формирующий JSON ответ для GET запроса. Достаточно переопределить
    get_ajax_data и вернуть в нем словарь
    '''

    def post(self, request, *args, **kwargs):
        data = self.get_ajax_data(**kwargs)
        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), mimetype='application/json')


#-------------------------------------------------------------------------------
class AjaxFormMixin(object):
    def json_response(self, response):
        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), mimetype='application/json')

    def get_ajax_invalid(self, form):
        response = {
            'status': False,
            'field_errors': form.errors,
            'non_field_errors': form.non_field_errors(),
        }

        # Ошибки из FormsetMixin
        formsets = getattr(form, 'formsets', {})
        for name, formset_option in formsets.items():
            formset, fk_name, model = formset_option
            formsets_errors = response.get('formsets_errors', {})
            if formset.errors:
                formsets_errors[name] = formset.errors
            response['formsets_errors'] = formsets_errors

        return response

    def get_ajax_valid(self, form):
        response = {
            'status': True
        }
        return response

    def form_invalid(self, form):
        result = super(AjaxFormMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.json_response(self.get_ajax_invalid(form))
        return result

    def form_valid(self, form):
        result = super(AjaxFormMixin, self).form_valid(form)
        if self.request.is_ajax():
            return self.json_response(self.get_ajax_valid(form))
        return result


class AjaxListMixin(ListView, AjaxDataMixin):
    '''
    Миксин, формирующий JSON ответ для GET запроса. Достаточно переопределить
    get_ajax_data и вернуть в нем словарь
    '''

    def get(self, request, *args, **kwargs):
        response = super(AjaxListMixin, self).get(request, request, *args, **kwargs)
        if request.is_ajax():
            data = self.get_ajax_data(object_list=self.object_list, **kwargs)
            return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), mimetype='application/json')
        else:
            return response


class SharedView(View):
    views = []

    def dispatch(self, request, *args, **kwargs):
        for v in self.views:
            if v.model.objects.filter(**kwargs).count() > 0:
                if v.menu_path:
                    request.menu_path = v.menu_path
                return v.as_view()(request, *args, **kwargs)
        return HttpResponseNotFound()
