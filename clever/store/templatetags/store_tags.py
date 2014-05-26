# -*- coding: utf-8 -*-
from clever.magic import get_model_fullname
from coffin import template
from django.core.urlresolvers import reverse
from clever.store.settings import CLEVER_CART_NAMESPACE

register = template.Library()


def add_query_to_url(url, **params):
    import urllib
    import urlparse

    url_parts = list(urlparse.urlparse(url))
    url_parts[4] = urllib.urlencode(params)

    return urlparse.urlunparse(url_parts)


@register.object
def add_to_cart_link(product, options=[], next=None):
    """ Создание url для добавления в корзину """
    url = reverse('%s:add-cart-item' % CLEVER_CART_NAMESPACE, kwargs={
        'content_type': get_model_fullname(product),
        'id': product.id
    })
    # TODO: Добавление опций в url
    return add_query_to_url(url, next=next)


@register.object
def remove_from_cart_link(item, next=None):
    url = reverse('%s:delete-cart-item' % CLEVER_CART_NAMESPACE, kwargs={
        'id': item.id
    })
    return add_query_to_url(url, next=next)


@register.object
def update_cart_item_url(item):
    return reverse('%s:update-cart-item' % CLEVER_CART_NAMESPACE, kwargs={
        'id': item.id
    })