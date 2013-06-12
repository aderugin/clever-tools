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
    pass


# ------------------------------------------------------------------------------
@AttributeManager.register_control(tag='range', verbose_name=u'Диапазон значений', allowed_only=True)
class RangeControl(AttributeControl):
    template_name = 'blocks/input/range.html'

    def __init__(self, *args, **kwargs):
        self.template_name = kwargs.pop('template_name', self.template_name)
        super(self.__class__, self).__init__(*args, **kwargs)

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
