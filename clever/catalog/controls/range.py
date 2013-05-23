# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from django import forms
from django.template.loader import render_to_string
from django.forms.fields import EMPTY_VALUES
from django.utils.translation import ugettext as _


class Range(forms.MultiWidget):
    def __init__(self, widget_from, widget_to, *args, **kwargs):
        widgets = (widget_from, widget_to)

        super(Range, self).__init__(widgets=widgets, *args, **kwargs)

    def decompress(self, value):
        return value

    def format_output(self, rendered_widgets):
        widget_context = {'min': rendered_widgets[0], 'max': rendered_widgets[1]}
        return render_to_string('blocks/input/range.html', widget_context)


class RangeField(forms.MultiValueField):
    default_error_messages = {
        'invalid_start': _(u'Enter a valid start value.'),
        'invalid_end': _(u'Enter a valid end value.'),
    }
    range = None

    def __init__(self, field_class, widget=forms.TextInput, *args, **kwargs):
        if not 'initial' in kwargs:
            kwargs['initial'] = ['', '']
        self.range = kwargs.pop('range', [0, 100])

        widget_from = forms.TextInput(attrs={'class': "b-filter__input", 'placeholder': "от"})
        widget_to = forms.TextInput(attrs={'class': "b-filter__input", 'placeholder': "до"})
        fields = (field_class(), field_class())

        super(RangeField, self).__init__(
            fields=fields,
            widget=Range(widget_from, widget_to),
            *args, **kwargs
        )

    def compress(self, data_list):
        if data_list:
            return [self.fields[0].clean(data_list[0]), self.fields[1].clean(data_list[1])]

        return None


class RangeControl:
    tag = 'range'
    name = u"Диапазон значений"
    empty_label = u"----"

    def create_form_field(self, attribute, values):
        max_value = max([v for v, t in values])
        min_value = min([v for v, t in values])

        return RangeField(
            forms.CharField,
            required=False,
            range=[min_value, max_value],
            label=attribute.title,
        )

    def create_query_part(self, attribute, values):
        query = {attribute.query_name + '__range': values}
        return models.Q(**query)

    def create_form_value(self, values):
        return values
