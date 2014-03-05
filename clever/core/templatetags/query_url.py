# -*- coding: utf-8 -*-
from django.utils.safestring import mark_safe
from django import template
from urlparse import parse_qs
from urllib import urlencode
from urllib import quote
from urlparse import urlparse

register = template.Library()


def quote_utf8(string, safe='/'):
      # reserved    = gen-delims / sub-delims

      # gen-delims  = ":" / "/" / "?" / "#" / "[" / "]" / "@"

      # sub-delims  = "!" / "$" / "&" / "'" / "(" / ")"
      #             / "*" / "+" / "," / ";" / "="

    # string = string.encode(encoding, errors)
    return unicode(quote(string.encode('utf-8')))


def urlencode_utf8(params, doseq=True):
    string = []
    for key, value in params.items():
        if not isinstance(value, (list, set)):
            value = (value,)
        for simple in value:
                string.append(u"=".join([quote_utf8(key), quote_utf8(simple)]))
    query = u"&".join(string)
    # import pdb; pdb.set_trace()
    return query


def get_query(query, new_params=None, remove_params=None):
    """
    Add and remove query parameters. From `django.contrib.admin`.
    """
    new_params = new_params if new_params is not None else {}
    remove_params = remove_params.split(',') if remove_params is not None else []
    # import pdb; pdb.set_trace()
    if not isinstance(query, dict):
        params = parse_qs(query, keep_blank_values=True)
    else:
        # import pdb; pdb.set_trace()
        params = dict(query)

    for key in remove_params:
        if key in params:
            del params[key]

    return urlencode_utf8(params)


@register.filter
def add_query(query, add):
    raise NotImplementedError()

@register.filter
def remove_query(query, remove):
    return get_query(query, None, remove)

@register.filter
def normalize_query(query):
    params = parse_qs(query, keep_blank_values=False)
    # import pdb; pdb.set_trace()
    return urlencode_utf8(params, doseq=True)

@register.filter
def get_path(url):
    url = urlparse(url)
    return url.path
