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
        self.request.cart.add(self.object, count=count, options=[])


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


# # ------------------------------------------------------------------------------
# class CartMixin(View):
#     cart_class = Cart
#     cart = None
#
#     def get_cart(self):
#         if not self.cart:
#             self.cart = self.cart_class.load(self.request)
#         return self.cart
#
#     def get(self, request, *args, **kwargs):
#         result = super(CartMixin, self).get(request, *args, **kwargs)
#         self.get_cart().save(self.request)
#         return result
#
#     def get_context_data(self, **kwargs):
#         context = super(CartMixin, self).get_context_data(**kwargs)
#         context['cart'] = self.get_cart()
#         return context
#
#
# # ------------------------------------------------------------------------------
# class BackRedirectMixin(CartMixin, RedirectView):
#     ''' Вспомогательный вид для последущего редиректа '''
#     permanent = False
#     url = '/cart/'
#
#     def get_redirect_url(self, **kwargs):
#         default_url = super(BackRedirectMixin, self).get_redirect_url(**kwargs)
#         redirect_url = self.request.REQUEST.get('back', default_url)
#         return redirect_url
#
#     def get(self, request, *args, **kwargs):
#         self.execute()
#         return super(BackRedirectMixin, self).get(request, request, *args, **kwargs)
#
#     def execute(self):
#         raise NotImplementedError
#
#
# # ------------------------------------------------------------------------------
# class AddProductView(AjaxMixin, BackRedirectMixin):
#     ''' Контроллер для добавление продукта в корзину '''
#     def execute(self):
#         try:
#             product = Product.objects.get(id=long(self.kwargs.get('id', None)))
#             self.get_cart().add_product(product, int(self.request.REQUEST.get('quantity', 1)))
#         except Product.DoesNotExist:
#             pass
#         except ValueError:
#             pass
#
#     def get_ajax_data(self, **kwargs):
#         return {'ok': True}
#
#
# # ------------------------------------------------------------------------------
# class UpdateProductView(AjaxMixin, BackRedirectMixin):
#     ''' Контроллер для обновления количества продукта в корзине '''
#     def execute(self):
#         try:
#             product = Product.objects.get(id=long(self.kwargs.get('id', None)))
#             self.get_cart().update_item_quantity(product, int(self.request.REQUEST.get('quantity', 1)))
#         except Product.DoesNotExist:
#             pass
#         except ValueError:
#             pass
#
#     def get_ajax_data(self, **kwargs):
#         return {'ok': True}
#
#
# # ------------------------------------------------------------------------------
# class RemoveProductView(AjaxMixin, BackRedirectMixin):
#     ''' Контроллер для удаления продукта из корзины '''
#     def execute(self):
#         try:
#             product = Product.objects.get(id=long(self.kwargs.get('id', None)))
#             self.get_cart().remove_product(product)
#         except Product.DoesNotExist:
#             pass
#         except ValueError:
#             pass
#
#     def get_ajax_data(self, **kwargs):
#         return {'ok': True}
#
#
# # ------------------------------------------------------------------------------
# class CartView(CartMixin, TemplateView):
#     ''' Контроллер для просмотра элементов в корзине '''
#     checkout_form = CheckoutForm
#
#     def get_checkout_kwargs(self):
#         return {}
#
#     def get_checkout_form(self):
#         form_kwargs = self.get_checkout_kwargs()
#         return self.checkout_form(self.request, **form_kwargs)
#
#     def get_deliveries_queryset(self):
#         return Delivery.objects.order_by('sort').all()
#
#     def get_payments_queryset(self):
#         return Payment.objects.order_by('sort').all()
#
#     def render_to_response(self, context):
#         if not len(self.get_cart()):
#             return redirect('/')
#         return super(CartView, self).render_to_response(context)
#
#     def get_context_data(self, **kwargs):
#         context = super(CartView, self).get_context_data(**kwargs)
#
#         context['form'] = self.get_checkout_form()
#         context['deliveries'] = self.get_deliveries_queryset()
#         context['payments'] = self.get_payments_queryset()
#         return context
#
#
# # ------------------------------------------------------------------------------
# class CheckoutView(CartMixin, CreateView):
#     form = CheckoutForm
#
#     def get_form(self, form_class):
#         return form_class(self.request, **self.get_form_kwargs())
#