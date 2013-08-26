# -*- coding: utf-8 -*-

from django import template
from clever.settings import get_option as get_settings_option

register = template.Library()


@register.filter
def get_option(name):
    param = get_settings_option(name)
    return param if param is not None else ''

# @register.simple_tag(takes_context=True)
# def show_recently_viewed(context, template_name='catalog/blocks/recent-viewed.html'):
#     someclass = load_class(CLEVER_RECENTLY_VIEWED)

#     # Render template
#     recent = someclass.load(context['request'])
#     if 'object' in context and isinstance(context['object'], Product.get_deferred_instance()):
#         recent.add_exclude(context['object'].id)
#     context = context.__copy__()
#     context.update({
#         'request': context['request'],
#         'products': recent.get_ordered_objects(),
#     })
#     t = template.loader.get_template(template_name)
#     return t.render(context)
