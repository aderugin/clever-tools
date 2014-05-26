# -*- coding: utf-8 -*-
"""
:mod:`clever.store.view` -- Виды для базовой корзины
========================================================

В данном модуле хранится базовый набор видов для работы с корзиной и заказами.

"""

from __future__ import absolute_import
from clever.magic import get_model_by_name
from django.db.models.loading import get_model
from django.http.response import Http404
from clever.core.views import AjaxNextView
from django.views import generic


class AddView(AjaxNextView):
    @property
    def object(self):
        model_class = get_model_by_name(self.kwargs['content_type'])
        if not model_class:
            raise Http404()
        return model_class.objects.get(id=self.kwargs['id'])

    def process(self, *args, **kwargs):
        # TODO: Add options
        try:
            count = max(0, int(self.request.GET.get('count', 1)))
        except TypeError:
            count = 0
        self.request.cart.add(self.object, count=count, options=self.request.GET.get('options', {}))


class AddBatchView(AjaxNextView):
    formset = None

    def process(self, *args, **kwargs):
        formset = self.formset(self.request.POST, self.request.FILES)
        if formset.is_valid():
            for item_data in formset.cleaned_data:
                if item_data['count'] > 0:
                    self.request.cart.add(item_data['product'], item_data['count'], options=item_data['options'])


class DeleteView(AjaxNextView):
    def process(self, *args, **kwargs):
        self.request.cart.delete(self.kwargs.get('id'))


class UpdateView(AjaxNextView):
    def process(self, *args, **kwargs):
        try:
            count = max(0, int(self.request.GET.get('count', 0)))
        except TypeError:
            count = 0
        self.request.cart.update(self.kwargs.get('id'), count=count)

    def get_ajax_data(self, **kwargs):
        cart = self.request.cart

        def item_to_json(item):
            return {
                'id': item.id,
                'price': item.price,
                'total_price': item.total_price
            }

        return {
            'success': True,
            'price': cart.price,
            'items': [item_to_json(item) for item in cart]
        }


class CartView(generic.TemplateView):
    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        return context
