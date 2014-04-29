# -*- coding: utf-8 -*-
from clever.markup.extensions import PageExtension
from clever.store.cart import CartBase, ItemBase


class CartExtension(PageExtension):
    cart = None

    def process_data(self, data):
        self.cart = CartBase(item_class=ItemBase)

        cart_data = data.get('cart', {})
        for i, item_data in enumerate(self.factory.convert(cart_data.get('products', []))):
            item = ItemBase(i, item_data['product'], item_data.get('count', 1), item_data.get('options', []))

            for key, value in item_data.items():
                if key not in ['id', 'product', 'count', 'options']:
                    try:
                        setattr(item, key, value)
                    except AttributeError:
                        pass

    def process_page(self, page, request, context):
        if page.params.get('is_cart', True):
            request.cart = self.cart
        else:
            request.cart = CartBase()
