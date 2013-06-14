# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from clever.catalog.attributes import AttributeControl
from clever.catalog.attributes import AttributeManager
from clever.forms.utils import FilterFieldMixin
from django.utils.encoding import smart_text, force_text

# ------------------------------------------------------------------------------
class Select(forms.Select):
    pass


# ------------------------------------------------------------------------------
class SelectField(FilterFieldMixin, forms.ChoiceField):
    widget = Select

    def filter(self, value):
        for k, v in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == smart_text(k2):
                        return value
            else:
                if value == smart_text(k):
                    return value
        return None


# ------------------------------------------------------------------------------
@AttributeManager.register_control(tag='select', verbose_name=u'Выпадающий список', allowed_only=True)
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
