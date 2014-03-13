# -*- coding: utf-8 -*-

# from django import template
from django import template
from clever.settings import get_option as get_settings_option

register = template.Library()

def get_option(name, default=None):
    param = get_settings_option(name, default)
    return param if param is not None else ''

register.filter(get_option)
