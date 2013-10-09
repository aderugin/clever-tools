# -*- coding: utf-8 -*-

from django import template
from django.template import loader
from ..models import Slider
from ..models import Item

register = template.Library()


@register.simple_tag(takes_context=True)
def slider(context, slug, template_name):
    if slug:
        sliders = Slider.objects.filter(active=True, slug=slug)
        if sliders.count() > 0:
            slider = sliders[0]
            items = Item.objects.filter(slider_id=slider.id, active=True)

            if items.count():
                t = loader.get_template(template_name)
                return t.render(template.RequestContext(context['request'], {
                    'slider': slider,
                    'items': items,
                }))
    return ""
