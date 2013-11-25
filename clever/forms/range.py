# -*- coding: utf-8 -*-
from django import forms
from django.forms.fields import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string


# ------------------------------------------------------------------------------
class RangeWidget(forms.MultiWidget):
    template_name = 'blocks/input/range.html'

    def __init__(self, widget_from, widget_to, *args, **kwargs):
        widgets = (widget_from, widget_to)
        template_name = kwargs.pop('template_name', None)
        if template_name:
            self.template_name = template_name

        super(RangeWidget, self).__init__(widgets=widgets, *args, **kwargs)

    def decompress(self, value):
        return value

    def format_output(self, rendered_widgets):
        widget_context = {
            'min': rendered_widgets[0],
            'max': rendered_widgets[1]
        }
        return render_to_string(self.template_name, widget_context)


# ------------------------------------------------------------------------------
class RangeField(forms.MultiValueField):
    default_error_messages = {
        'invalid_start': _(u'Enter a valid start value.'),
        'invalid_end': _(u'Enter a valid end value.'),
    }
    range = None

    def __init__(self, field=forms.CharField(), widget=RangeWidget, *args, **kwargs):
        if not 'initial' in kwargs:
            kwargs['initial'] = ['', '']
        self.range = kwargs.pop('range', [0, 100])

        fields = kwargs.pop('fields',  (field, field))

        super(RangeField, self).__init__(
            fields=fields,
            widget=widget(fields[0].widget, fields[1].widget, template_name=kwargs.pop('template_name', None)),
            *args, **kwargs
        )

    def compress(self, data_list):
        if data_list:
            return [self.fields[0].clean(data_list[0]), self.fields[1].clean(data_list[1])]

        return None
