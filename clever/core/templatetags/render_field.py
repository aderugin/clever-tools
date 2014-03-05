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

# class RenderFieldExtension(Extension):
#     tags = set(['render_field'])

#     def parse(self, parser):
#         lineno = parser.stream.next().lineno
#         kindarg = parser.parse_expression()

#         # # Allow kind to be defined as jinja2 name node
#         # if isinstance(kindarg, nodes.Name):
#         #     kindarg = nodes.Const(kindarg.name)
#         args = [kindarg]
#         # if args[0].value not in self.compressors:
#         #     raise TemplateSyntaxError('compress kind may be one of: %s' %
#         #                               (', '.join(self.compressors.keys())),
#         #                               lineno)
#         # if parser.stream.skip_if('comma'):
#         #     modearg = parser.parse_expression()
#         #     # Allow mode to be defined as jinja2 name node
#         #     if isinstance(modearg, nodes.Name):
#         #         modearg = nodes.Const(modearg.name)
#         #         args.append(modearg)
#         # else:
#         #     args.append(nodes.Const('file'))
#         # body = parser.parse_statements(['name:endcompress'], drop_needle=True)
#         # parser.parse_statements([], drop_needle=True)
#         return self.call_method('_compress', args).set_lineno(lineno)

#     def _compress(self, kind, mode, caller):
#         import ipdb; ipdb.set_trace()
#         pass
#     #     # This extension assumes that we won't force compression
#     #     forced = False

#     #     mode = mode or OUTPUT_FILE
#     #     original_content = caller()
#     #     context = {
#     #         'original_content': original_content
#     #     }
#     #     return self.render_compressed(context, kind, mode, forced=forced)

#     # def get_original_content(self, context):
#     #     return context['original_content']

# register.tag(RenderFieldExtension)

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
def render_label(field, classes=[], **kwargs):
    if field == None:
        return ''
    return Markup(field.label_tag())

@register.object
def render_field(field, template=None, **kwargs):
    if field == None:
        return ''

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
