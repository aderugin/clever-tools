# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from clever.catalog.attributes import AttributeControl
from clever.catalog.attributes import AttributeManager
from clever.catalog import settings


# ------------------------------------------------------------------------------
class Checkbox(forms.CheckboxSelectMultiple):
    pass


# ------------------------------------------------------------------------------
class CheckboxField(forms.MultipleChoiceField):
    widget = Checkbox

    def validate(self, *args, **kwargs):
        pass


# ------------------------------------------------------------------------------
@AttributeManager.register_control(tag='checkbox', verbose_name=u'Флажки', allowed_only=True)
class CheckboxControl(AttributeControl):
    template_name = settings.CLEVER_FILTER_CHECKBOX_TEMPLATE
    empty_label = settings.CLEVER_EMPTY_LABEL

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
