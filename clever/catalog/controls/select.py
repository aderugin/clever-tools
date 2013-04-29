# -*- coding: utf-8 -*-

from django import forms
from django.db import models


# class RadioFilter(forms.CheckboxSelectMultiple):
#     pass


# class RadioFilterField(forms.ChoiceField):
#     widget = RadioFilter


class SelectControl:
    tag = 'select'
    name = u"Выпадающий список"
    empty_label = u"----"

    def create_form_field(self, attribute, values):
        return forms.ChoiceField(
            choices=[(u'', self.empty_label)] + list(values),
            label=attribute.title,
            required=False,
        )

    def create_query_part(self, attribute, values):
        query = {attribute.query_name: values}
        return models.Q(**query)

    def create_form_value(self, values):
        return values
