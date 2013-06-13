# -*- coding: utf-8 -*-
from django.utils.safestring import mark_safe
from django import template
from urlparse import urlparse

register = template.Library()


def get_query(p, new_params=None, remove=None):
    """
    Add and remove query parameters. From `django.contrib.admin`.
    """
    if new_params is None:
        new_params = {}
    if remove is None:
        remove = []
    for r in remove:
        for k in p.keys():
            if k.startswith(r):
                del p[k]
    for k, v in new_params.items():
        if k in p and v is None:
            del p[k]
        elif v is not None:
            p[k] = v
    return mark_safe(
        '&amp;' +
        '&amp;'.join([u'%s=%s' % (k, v) for k, v in p.items()])
               .replace(' ', '%20')
    )


def string_to_dict(string, separator=','):
    """
    Usage::

        {{ url|string_to_dict:"width=10,height=20" }}
        {{ url|string_to_dict:"width=10" }}
        {{ url|string_to_dict:"height=20" }}
    """
    kwargs = {}
    if string:
        string = str(string)
        if separator not in string:
            # ensure at least one separator
            string += separator
        for arg in string.split(separator):
            arg = arg.strip()
            if arg == '':
                continue
            kw, val = arg.split('=', 1)
            kwargs[kw] = val
    return kwargs


def string_to_list(string):
    """
    Usage::

        {{ url|thumbnail:"width,height" }}
    """
    args = []
    if string:
        string = str(string)
        if ',' not in string:
            # ensure at least one ','
            string += ','
        for arg in string.split(','):
            arg = arg.strip()
            if arg == '':
                continue
            args.append(arg)
    return args


@register.filter
def add_query(var, add):
    add = string_to_dict(add)
    params = string_to_dict(var, '&')
    return get_query(params, add, None)


@register.filter
def remove_query(var, remove):
    remove = string_to_list(remove)
    params = string_to_dict(var, '&')
    # import pdb; pdb.set_trace()
    return get_query(params, None, remove)


@register.filter
def get_path(url):
    url = urlparse(url)
    return url.path
