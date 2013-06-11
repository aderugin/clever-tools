# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from clever.catalog.attributes import AttributeControl
from clever.catalog.attributes import AttributeManager


# ------------------------------------------------------------------------------
class Checkbox(forms.CheckboxSelectMultiple):
    pass


# ------------------------------------------------------------------------------
class CheckboxField(forms.MultipleChoiceField):
    widget = Checkbox


# ------------------------------------------------------------------------------
@AttributeManager.register_control(tag='checkbox', verbose_name=u'Флажки')
class CheckboxControl(AttributeControl):
    empty_label = u"----"

    def create_form_field(self, attribute, values):
        return CheckboxField(
            choices=list(values),
            label=attribute.title,
            required=False,
        )

    def create_query_part(self, attribute, values):
        query = {attribute.query_name + '__in': values}
        return models.Q(**query)

    def create_form_value(self, values):
        return values
