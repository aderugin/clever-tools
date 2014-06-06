# -*- coding: utf-8 -*-
from django import template
from django.utils.encoding import force_unicode
import re
import json

register = template.Library()


@register.filter()
def format_intspace(value):
    """
    Converts an integer to a string containing spaces every three digits.
    For example, 3000 becomes '3 000' and 45000 becomes '45 000'.
    See django.contrib.humanize app
    """
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1> \g<2>', orig)
    if orig == new:
        return new
    else:
        return format_intspace(new)

@register.filter()
def to_str(value):
    return str(value)


@register.filter()
def widget_name(field):
    return field.field.widget.__class__.__name__


@register.filter()
def to_json(value):
    return json.dumps(value, ensure_ascii=False)
