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
from . import signals


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

    def get_ajax_data(self, **kwargs):
        context = self.request.cart.to_json()
        context.update({
            'status': True
        })
        return context

class AddBatchView(AjaxNextView):
    formset = None

    def process(self, *args, **kwargs):
        formset = self.formset(self.request.POST, self.request.FILES)
        if formset.is_valid():
            for item_data in formset.cleaned_data:
                if item_data['count'] > 0:
                    self.request.cart.add(item_data['product'], item_data['count'], options=item_data['options'])

    def get_ajax_data(self, **kwargs):
        context = self.request.cart.to_json()
        context.update({
            'status': True
        })
        return context


class DeleteView(AjaxNextView):
    def process(self, *args, **kwargs):
        self.request.cart.delete(self.kwargs.get('id'))

    def get_ajax_data(self, **kwargs):
        context = self.request.cart.to_json()
        context.update({
            'status': True
        })
        return context


class UpdateView(AjaxNextView):
    def process(self, *args, **kwargs):
        try:
            count = max(0, int(self.request.GET.get('count', 0)))
        except TypeError:
            count = 0
        self.request.cart.update(self.kwargs.get('id'), count=count)

    def get_ajax_data(self, **kwargs):
        context = self.request.cart.to_json()
        context.update({
            'status': True
        })
        return context


class CartView(generic.CreateView):
    order_field = 'order'

    def form_valid(self, form):
        order = form.instance
        cart = self.request.cart

        # send pre signal
        signals.pre_order_create.send(order, order=order, cart=cart)

        # fill items and order
        items = self.populate_order(order, cart)
        response = super(CartView, self).form_valid(form)

        # save items
        for item in items:
            setattr(item, 'order', order)
            item.save()

        # send post signal
        signals.post_order_create.send(order, order=order, cart=cart)

        # Clear cart
        cart.clear()
        return response

    def populate_order(self, order, cart):
        raise NotImplementedError("Populate order from cart is not implemented")
