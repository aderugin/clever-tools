# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from django import forms
from django.template.loader import render_to_string
from clever.forms import RangeWidget
from clever.forms import RangeField
from clever.catalog.attributes import AttributeControl
from clever.catalog.attributes import AttributeManager


# ------------------------------------------------------------------------------
class Range(RangeWidget):
    def format_output(self, rendered_widgets):
        widget_context = {'min': rendered_widgets[0], 'max': rendered_widgets[1]}
        return render_to_string('blocks/input/range.html', widget_context)


# ------------------------------------------------------------------------------
@AttributeManager.register_control(tag='range', verbose_name=u'Диапазон значений')
class RangeControl(AttributeControl):
    def create_form_field(self, attribute, values):
        type = attribute.type_object
        if len(values) > 0:
            max_value = max([type.filter_value(v) for v, t in values])
            min_value = min([type.filter_value(v) for v, t in values])
        else:
            max_value = 0
            min_value = 0

        return RangeField(
            widget=Range,
            fields=[
                forms.CharField(widget=forms.TextInput(attrs={'class': "b-filter__input", 'placeholder': "от"})),
                forms.CharField(widget=forms.TextInput(attrs={'class': "b-filter__input", 'placeholder': "до"}))
            ],
            required=False,
            range=[min_value, max_value],
            label=attribute.title,
        )

    def create_query_part(self, attribute, values):
        query = {attribute.query_name + '__range': values}
        return models.Q(**query)

    def create_form_value(self, values):
        return values

    @property
    def is_range(self):
        return True
