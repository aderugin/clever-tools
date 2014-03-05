# -*- coding: utf-8 -*-

from django import template
from domino.apps.compare.models import Comparer

register = template.Library()


@register.inclusion_tag('catalog/blocks/compare_products.html', takes_context=True)
def show_compare_menu(context):
    request = context.get('request', None)
    comparer = Comparer.load(request)
    groups = comparer.get_groups('all')
    return {
        'groups': groups,
        'request': request
    }


@register.inclusion_tag('catalog/blocks/compare_status_productview.html', takes_context=True)
def compare_status_productview(context):
    request = context.get('request', None)
    product = context.get('product', None)
    comparer = Comparer.load(request)

    if comparer.has(product):
        result = {
            'is_compared': True,
            'product_id': product.id
        }
    else:
        result = {
            'is_compared': False,
            'product_id': product.id
        }

    return result


@register.inclusion_tag('catalog/blocks/compare_status_productlist.html', takes_context=True)
def compare_status_productlist(context):
    request = context.get('request', None)
    product = context.get('product', None)
    comparer = Comparer.load(request)

    if comparer.has(product):
        result = {
            'is_compared': True,
            'product_id': product.id
        }
    else:
        result = {
            'is_compared': False,
            'product_id': product.id
        }

    return result
