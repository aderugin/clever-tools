# -*- coding: utf-8 -*-
from coffin import template
from coffin.interop import django_filter_to_jinja2
from jinja2 import nodes
from jinja2 import Markup
from jinja2.ext import Extension
from jinja2.exceptions import TemplateSyntaxError
from django.template.loader import render_to_string

register = template.Library()

try:
    from widget_tweaks.templatetags import widget_tweaks
except ImportError:
    pass
else:
    field_type = django_filter_to_jinja2(widget_tweaks.field_type)
    widget_type = django_filter_to_jinja2(widget_tweaks.widget_type)


def process_field_attributes(field, attr, process):
    # split attribute name and value from 'attr:value' string
    params = attr.split(':', 1)
    attribute = params[0]
    value = params[1] if len(params) == 2 else ''

    # decorate field.as_widget method with updated attributes
    old_as_widget = field.as_widget

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = attrs or {}
        process(widget or self.field.widget, attrs, attribute, value)
        return old_as_widget(widget, attrs, only_initial)

    bound_method = type(old_as_widget)
    try:
        field.as_widget = bound_method(as_widget, field, field.__class__)
    except TypeError:  # python 3
        field.as_widget = bound_method(as_widget, field)
    return field


def set_field_attribute(field, name, value):
    def process(widget, attrs, attribute, value):
        attrs[attribute] = value
    return process_field_attributes(field, name + ':' + value, process)

@register.object
def render_label(field, **kwargs):
    if field == None:
        return ''
    return Markup(field.label_tag(attrs=kwargs))


@register.object
def render_field(field, template=None, attrs={}, **kwargs):
    if field == None:
        return ''
    if attrs:
        kwargs.update(attrs)
    is_render = False
    if field.field.widget:
        widget = field.field.widget
        if template and hasattr(widget, 'template_name'):
            widget.template_name = template
        else:
            is_render = True

    for name, value in kwargs.items():
        field = set_field_attribute(field, name, value)

    if is_render and template:
        result = render_to_string(template, {
            'bound_field': field,
            'field': field.field,
            'widget': field.field.widget,
            'attributes': kwargs
        })
    else:
        result = field.as_widget()
    return Markup(result)
