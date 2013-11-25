# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from clever.catalog.attributes import AttributeControl
from clever.catalog.attributes import AttributeManager
from clever.catalog import settings


# ------------------------------------------------------------------------------
class RadioFilter(forms.CheckboxSelectMultiple):
    pass


# ------------------------------------------------------------------------------
class RadioFilterField(forms.MultipleChoiceField):
    widget = RadioFilter

    def validate(self, *args, **kwargs):
        pass

# ------------------------------------------------------------------------------
@AttributeManager.register_control(tag='radio', verbose_name=u'Переключатели', allowed_only=True)
class RadioControl(AttributeControl):
    template_name = settings.CLEVER_FILTER_RADIO_TEMPLATE
    empty_label = u"----"

    def create_form_field(self, attribute, values):
        return forms.RadioFilterField(
            choices=[(u'', self.empty_label)] + list(values),
            label=attribute.title,
            required=False,
        )

    def create_query_part(self, attribute, values):
        query = {attribute.query_name: values}
        return models.Q(**query)

    def create_form_value(self, values):
        return values
