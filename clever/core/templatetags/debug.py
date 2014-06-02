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
        str = pformat(value, indent=4, depth=2)
        res.append(u'%s: %s\n' % (key, str.decode("utf-8")))
    return Markup(u'<pre>' + u'\n'.join(res) + u'</pre>')