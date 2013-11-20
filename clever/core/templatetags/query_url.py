# -*- coding: utf-8 -*-
from django.utils.safestring import mark_safe
from django import template
from urlparse import parse_qs
from urllib import urlencode
from urlparse import urlparse

register = template.Library()


def get_query(url, new_params=None, remove_params=None):
    """
    Add and remove query parameters. From `django.contrib.admin`.
    """
    new_params    = new_params               if new_params    is not None else {}
    remove_params = remove_params.split(',') if remove_params is not None else []
    params = parse_qs(url, keep_blank_values=True)

    for key in remove_params:
        if key in params:
            del params[key]

    return urlencode(params, doseq=True)


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
def add_query(url, add):
    # add = string_to_dict(add)
    # params = string_to_dict(var, '&')
    # return get_query(params, add, None)
    raise NotImplementedError()

@register.filter
def remove_query(url, remove):
    # remove = string_to_list(remove)
    # params = string_to_dict(var, '&')
    # import pdb; pdb.set_trace()
    return get_query(url, None, remove)

@register.filter
def normalize_query(url):
    params = parse_qs(url, keep_blank_values=False)
    return urlencode(params, doseq=True)

@register.filter
def get_path(url):
    url = urlparse(url)
    return url.path
