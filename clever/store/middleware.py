# -*- coding: utf-8 -*-
from clever.store import settings
from clever.magic import load_class


class CartMiddleware(object):
    def load_cart(self, request):
        cart = request.session.get(settings.CLEVER_CART_SESSION_NAME, None)
        if cart is None:
            cart_class = load_class(settings.CLEVER_CART_CLASS)
            item_class = load_class(settings.CLEVER_CART_ITEM_CLASS)
            cart = cart_class(item_class=item_class)
        else:
            cart.cleanup()
        return cart

    def process_request(self, request):
        request.cart = self.load_cart(request)

    def process_response(self, request, response):
        # fixme: Почему у не которых запросов не вызывается process_request?
        cart = getattr(request, 'cart', None)
        if cart is not None and cart.is_modified:
            request.session[settings.CLEVER_CART_SESSION_NAME] = request.cart
            request.session.modified = True
        return response
