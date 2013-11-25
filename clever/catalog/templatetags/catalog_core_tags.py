# -*- coding: utf-8 -*-

from django import template
from django.template.loader import render_to_string
from clever.catalog.settings import CLEVER_RECENTLY_VIEWED
from clever.magic import load_class
from clever.catalog.models import Product

register = template.Library()


@register.simple_tag(takes_context=True)
def show_recently_viewed(context, template_name='catalog/blocks/recent-viewed.html'):
    someclass = load_class(CLEVER_RECENTLY_VIEWED)

    # Render template
    recent = someclass.load(context['request'])
    if 'object' in context and isinstance(context['object'], Product.get_deferred_instance()):
        recent.add_exclude(context['object'].id)
    context = context.__copy__()
    context.update({
        'request': context['request'],
        'products': recent.get_ordered_objects(),
    })
    t = template.loader.get_template(template_name)
    return t.render(context)


@register.simple_tag(takes_context=True)
def render_filter_attribute(context, attr, widget):
    attribute = attr.attribute
    control = attribute.control_object
    if control.is_template and control.template_name:
        context = context.__copy__()
        context.update({
            'attribute': attribute,
            'field': widget.field,
            'widget': widget
        })
        return render_to_string(control.template_name, context)
    return widget
