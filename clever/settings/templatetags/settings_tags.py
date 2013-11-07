# -*- coding: utf-8 -*-

from django import template
from clever.settings import get_option as get_settings_option

register = template.Library()


@register.filter
def get_option(name):
    param = get_settings_option(name)
    return param if param is not None else ''
