# -*- coding: utf-8 -*-

from django.views.generic import View
from django.views.generic import ListView
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
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
    def get_success_url(self):
        return ''

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
        if hasattr(self, 'success_message'):
            response['message'] = self.success_message
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
class BreadcrumbsMixin(object):
    def prepare_breadcrumbs(self, breadcrumbs, context):
        ''' Подготовка хлебных крошек '''
        pass

    def render_to_response(self, context, **response_kwargs):
        self.prepare_breadcrumbs(self.request.breadcrumbs, context)
        return super(BreadcrumbsMixin, self).render_to_response(context, **response_kwargs)


class DetailListView(ListView):
    allow_empty = False
    detail_model = None
    filter_attr = None

    def __init__(self, **kwargs):
        if not self.detail_model:
            raise ImproperlyConfigured("%s is missing detail_model" % self.__class__.__name__)
        if not self.filter_attr:
            raise ImproperlyConfigured("%s is missing filter_attr" % self.__class__.__name__)
        super(DetailListView, self).__init__(**kwargs)

    def get_queryset(self):
        kwargs = {}
        if 'pk' in self.kwargs and self.kwargs['pk']:
            kwargs['pk'] = self.kwargs['pk']
        if 'slug' in self.kwargs and self.kwargs['slug']:
            kwargs['slug'] = self.kwargs['slug']
        if len(kwargs) < 1:
            return []
        detail = self.detail_model.objects.filter(**kwargs)
        if detail.count() > 0:
            self.detail = detail.get()
            return super(DetailListView, self).get_queryset().filter(**{self.filter_attr: self.detail})
        return []

    def get_context_data(self, **kwargs):
        context = super(DetailListView, self).get_context_data(**kwargs)
        context['object'] = self.detail
        context[self.detail.__class__.__name__] = self.detail
        return context

    #-------------------------------------------------------------------------------


class SortableMixin(object):
    order_by = {
        # TODO: Добавить сортировку по идентификатору
    }
    default_order = None
    default_sort = 'asc'

    def get_order(self):
        order = self.request.GET.get('order_by', None)
        sort_by = self.request.GET.get('sort_by', self.default_sort)
        order_by = None

        if order and not order in self.order_by:
            order = self.default_order
        return order, sort_by

    def get_sortable_query(self, queryset):
        ''' Сортируем queryset перед выдачей '''
        order, sort_by = self.get_order()
        if order in self.order_by:
            order_by = self.order_by[order]
            result_order = []
            for field in order_by['fields']:
                if sort_by == 'desc':
                    if field[0] == '-':
                        field = field[1:]
                    else:
                        field = '-' + field
                result_order.append(field)
            queryset = queryset.order_by(*result_order)
        return queryset

    def get_order_params(self):
        ''' Получем информацию для сортировки '''
        order, sort_by = self.get_order()
        sort_list = []
        for key, params in self.order_by.items():
            sort_name = params['title']
            sort = 'asc'
            if order == key:
                sort = 'asc' if sort_by == 'desc' else 'desc'
            sort_list.append([sort_name, key, sort])
        return order, sort_by, sort_list

    def update_context_data(self, context):
        order, sort_by, sort_list = self.get_order_params()
        context.update({
            'order_by': order,
            'sort_by': sort_by,
            'sort_list': sort_list,
        })
        return context

    #-------------------------------------------------------------------------------


class SortableListMixin(SortableMixin):
    def get_queryset(self):
        queryset = super(SortableListMixin, self).get_queryset()
        return self.get_sortable_query(queryset)

    def get_context_data(self, **kwargs):
        context = super(SortableListMixin, self).get_context_data(**kwargs)
        return self.update_context_data(context)
