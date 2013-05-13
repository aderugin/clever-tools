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
from clever.store.cart import CartBase
# from django.views.generic import FormView


# ------------------------------------------------------------------------------
class BackRedirectMixin(RedirectView):
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


# ------------------------------------------------------------------------------
class CartMixin(View):
    cart_class = CartBase

    def get(self, request, *args, **kwargs):
        with self.cart_class.open(request) as cart:
            self.cart = cart
            return super(CartMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CartMixin, self).get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


# ------------------------------------------------------------------------------
class AddProductView(CartMixin, BackRedirectMixin):
    ''' Контроллер для добавление продукта в корзину '''
    def execute(self):
        try:
            product = Product.objects.get(id=self.kwargs.get('id', None))
            self.cart.add_product(product, int(self.request.REQUEST.get('quantity', 1)))
        except Product.DoesNotExist:
            pass


# ------------------------------------------------------------------------------
class RemoveProductView(CartMixin, BackRedirectMixin):
    ''' Контроллер для удаления продукта из корзины '''
    def execute(self):
        try:
            product = Product.objects.get(id=self.kwargs.get('id', None))
            self.cart.remove_product(product)
        except Product.DoesNotExist:
            pass


# ------------------------------------------------------------------------------
class CartView(CartMixin, TemplateView):
    ''' Контроллер для просмотра элементов в корзине '''
    pass
