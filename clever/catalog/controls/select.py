# -*- coding: utf-8 -*-

from django import forms
from django.db import models

class SelectControl:
    empty_label = u"----"

    def create_form_field(self, attribute, values):
        return forms.ChoiceField(
            choices=[(u'', self.empty_label)] + values,
            label=attribute.title,
            required=False,
        )

    def create_query_part(self, attribute, values):
        return models.Q(attributes__string_value=values)
