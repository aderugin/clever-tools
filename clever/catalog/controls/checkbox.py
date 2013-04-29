# -*- coding: utf-8 -*-

from django import forms
from django.db import models


class Checkbox(forms.CheckboxSelectMultiple):
    pass


class CheckboxField(forms.MultipleChoiceField):
    widget = Checkbox


class CheckboxControl:
    tag = 'checkbox'
    name = u"Флажок"
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
