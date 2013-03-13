# -*- coding: utf-8 -*-

from django import template
from ..cart import *
from pytils import numeral

register = template.Library()


@register.inclusion_tag('store/cart_box.html')
def store_cart_box(request):

    cart = get_user_cart(request)

    total_cost = cart.total_cost_with_sale()
    count = cart.get_count_items()
    count_plural = numeral.choose_plural(count, (u"товар", u"товара", u"товаров"))
    return {'total_cost': total_cost, 'count': count, 'cart': cart, 'count_plural': count_plural}
