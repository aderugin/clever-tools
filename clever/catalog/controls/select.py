# -*- coding: utf-8 -*-

from django import forms
from django.db import models


class Select(forms.Select):
    pass


class SelectField(forms.ChoiceField):
    widget = Select


class SelectControl:
    tag = 'select'
    name = u"Выпадающий список"
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
