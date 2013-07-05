# -*- coding: utf-8 -*-

from django import template
from clever.catalog.settings import CLEVER_RECENTLY_VIEWED
from clever.magic import load_class
register = template.Library()


@register.simple_tag(takes_context=True)
def show_recently_viewed(context, template_name='catalog/blocks/recent-viewed.html'):
    someclass = load_class(CLEVER_RECENTLY_VIEWED)

    # Render template
    recent = someclass.load(context['request'])
    t = template.loader.get_template(template_name)
    return t.render(template.Context({
        'request': context['request'],
        'products': recent.get_ordered_objects(),
    }))
