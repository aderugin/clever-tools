# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from django import forms
from django.template.loader import render_to_string
from clever.forms import RangeWidget
from clever.forms import RangeField
from clever.catalog.attributes import AttributeControl
from clever.catalog.attributes import AttributeManager
from clever.catalog import settings

# ------------------------------------------------------------------------------
class Range(RangeWidget):
    pass


# ------------------------------------------------------------------------------
@AttributeManager.register_control(tag='range', verbose_name=u'Диапазон значений', allowed_only=True)
class RangeControl(AttributeControl):
    is_template = False
    template_name = settings.CLEVER_FILTER_RANGE_TEMPLATE
    max_args = settings.CLEVER_FILTER_RANGE_MAX_ARGS
    min_args = settings.CLEVER_FILTER_RANGE_MIN_ARGS

    def __init__(self, *args, **kwargs):
        self.template_name = kwargs.pop('template_name', self.template_name)
        self.min_args = kwargs.pop('min_args', self.min_args)
        self.max_args = kwargs.pop('max_args', self.max_args)

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
            template_name=self.template_name,
            widget=Range,
            fields=[
                forms.CharField(widget=forms.TextInput(attrs=self.min_args)),
                forms.CharField(widget=forms.TextInput(attrs=self.max_args))
            ],
            required=False,
            range=[min_value, max_value],
            label=attribute.title,
        )

    def create_query_part(self, attribute, values):
        type = attribute.type_object
        if len(values) > 0:
            min_value = min([type.filter_value(values[0])])
            max_value = max([type.filter_value(values[1])])
        else:
            min_value = None
            max_value = None
        query = None
        if not min_value and max_value:
            query = {attribute.query_name + '__lte': max_value}
        elif not max_value and min_value:
            query = {attribute.query_name + '__gte': min_value}
        elif max_value and min_value:
            query = {attribute.query_name + '__range': values}

        if query:
            return models.Q(**query)
        return None

    def create_form_value(self, values):
        return values

    @property
    def is_range(self):
        return True
