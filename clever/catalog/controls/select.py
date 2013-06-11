# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from clever.catalog.attributes import AttributeControl
from clever.catalog.attributes import AttributeManager


# ------------------------------------------------------------------------------
class Select(forms.Select):
    pass


# ------------------------------------------------------------------------------
class SelectField(forms.ChoiceField):
    widget = Select


# ------------------------------------------------------------------------------
@AttributeManager.register_control(tag='select', verbose_name=u'Выпадающий список')
class SelectControl(AttributeControl):
    empty_label = u"----"

    def create_form_field(self, attribute, values):
        return SelectField(
            choices=[(u'', self.empty_label)] + list(values),
            label=attribute.title,
            required=False,
        )

    def create_query_part(self, attribute, values):
        query = {attribute.query_name: values}
        return models.Q(**query)

    def create_form_value(self, values):
        return values
