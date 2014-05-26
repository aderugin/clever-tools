# -*- coding: utf-8 -*-
import inspect
from pprint import pformat
from coffin.template import Library
from jinja2 import Markup

register = Library()


@register.filter()
def dir(value):
    res = []
    for key, value in inspect.getmembers(value):
        res.append('%r: %s\n' % (key, pformat(value, indent=4, depth=2)))
    return Markup('<pre>' + '\n'.join(res) + '</pre>')