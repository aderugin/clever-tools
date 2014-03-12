# -*- coding: utf-8 -*-
from clever.markup.extensions import PageExtension
# from clever.cart import Cart as CartBase

class Cart:
    products = []

    def __iter__(self):
        return iter(self.products)

    def __len__(self):
        return len(self.products)


class CartExtension(PageExtension):
    cart = None

    def process_data(self, data):
        self.cart = Cart()
        cart_data = data.get('cart', {})
        self.cart.products = self.factory.convert(cart_data.get('products', []))
        self.cart.total_price = sum(map(lambda x: x['price'], self.cart.products))

    def process_page(self, page, request, context):
        if page.params.get('is_cart', True):
            request.cart = self.cart
        else:
            request.cart = Cart()
