# -*- coding: utf-8 -*-
"""
:mod:`clever.store.view` -- Виды для базовой корзины
========================================================

В данном модуле хранится базовый набор видов для работы с корзиной и заказами.

"""

from __future__ import absolute_import
from django.views.generic.base import View
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
from clever.catalog.models import Product
from clever.store import Cart
# from django.views.generic import FormView
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
import json
from clever.core.views import AjaxMixin

# ------------------------------------------------------------------------------
class CartMixin(View):
    cart_class = Cart
    cart = None

    def get_cart(self):
        if not self.cart:
            self.cart = self.cart_class.load(self.request)
        return self.cart

    def get(self, request, *args, **kwargs):
        result = super(CartMixin, self).get(request, *args, **kwargs)
        self.get_cart().save(self.request)
        return result

    def get_context_data(self, **kwargs):
        context = super(CartMixin, self).get_context_data(**kwargs)
        context['cart'] = self.get_cart()
        return context


# ------------------------------------------------------------------------------
class BackRedirectMixin(CartMixin, RedirectView):
    ''' Вспомогательный вид для последущего редиректа '''
    permanent = False

    def get_redirect_url(self, **kwargs):
        default_url = super(BackRedirectMixin, self).get_redirect_url(**kwargs)
        redirect_url = self.request.REQUEST.get('back', default_url)
        return redirect_url

    def get(self, request, *args, **kwargs):
        self.execute()
        return super(BackRedirectMixin, self).get(request, request, *args, **kwargs)

    def execute(self):
        raise NotImplementedError

#
#class AjaxMixin(View):
#    '''
#    Миксин, формирующий JSON ответ. Достаточно переопределить
#    get_ajax_data и вернуть в нем словарь
#    '''
#    def get_ajax_data(self, **kwargs):
#        return { }
#
#    def get(self, request, *args, **kwargs):
#        super(AjaxMixin, self).get(request, request, *args, **kwargs)
#        data = self.get_ajax_data(**kwargs)
#        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), mimetype='application/json')

# ------------------------------------------------------------------------------
class AddProductView(AjaxMixin, BackRedirectMixin):
    ''' Контроллер для добавление продукта в корзину '''
    def execute(self):
        try:
            product = Product.objects.get(id=self.kwargs.get('id', None))
            self.get_cart().add_product(product, int(self.request.REQUEST.get('quantity', 1)))
        except Product.DoesNotExist:
            pass

    def get_ajax_data(self, **kwargs):
        return {'ok': True}


# ------------------------------------------------------------------------------
class RemoveProductView(BackRedirectMixin):
    ''' Контроллер для удаления продукта из корзины '''
    def execute(self):
        try:
            product = Product.objects.get(id=self.kwargs.get('id', None))
            self.get_cart().remove_product(product)
        except Product.DoesNotExist:
            pass


# ------------------------------------------------------------------------------
class CartView(CartMixin, TemplateView):
    ''' Контроллер для просмотра элементов в корзине '''
    pass
