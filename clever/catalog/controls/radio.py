# -*- coding: utf-8 -*-

from django import forms
from django.db import models


class RadioFilter(forms.CheckboxSelectMultiple):
    pass


class RadioFilterField(forms.MultipleChoiceField):
    widget = RadioFilter


class RadioControl:
    tag = 'radio'
    name = u"Выбор одного элемента"
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
