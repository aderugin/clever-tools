# -*- coding: utf-8 -*-
from django import template
register = template.Library()


@register.filter
def is_equal(value, other):
    return value == other


@register.filter
def is_noteequal(value, other):
    return value != other
