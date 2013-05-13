# -*- coding: utf-8 -*-

from django import template
from clever.store.cart import Cart

register = template.Library()


@register.inclusion_tag('blocks/header-cart.html', takes_context=True)
def store_cart_box(context):
    request = context.get('request', None)
    with Cart.load(request) as cart:
        return {
            'cart': cart
        }
