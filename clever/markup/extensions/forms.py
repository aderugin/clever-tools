# -*- coding: utf-8 -*-
from clever.markup.extensions import FixtureExtension
from clever.markup.extensions import FixtureMetadata
from clever.forms import range as clever_range
from django import forms

def create_field(field_class, widget=None):
    def ctor(*args, **kwargs):
        if widget:
            kwargs['widget'] = widget
        return field_class(*args, **kwargs)
    return ctor

def create_range(*args, **kwargs):
    return clever_range.RangeField(*args, **kwargs)

FIELDS = {
    'string': create_field(forms.CharField),
    'text': create_field(forms.TextInput),
    'checkbox': create_field(forms.ChoiceField, widget=forms.CheckboxInput),
    'select': create_field(forms.ChoiceField, widget=forms.Select),
    'radio': create_field(forms.ChoiceField, widget=forms.RadioSelect),
    'checkboxes': create_field(forms.MultipleChoiceField, widget=forms.CheckboxSelectMultiple),
    'range': create_range
}

def create_range():
    pass


class FormExtension(FixtureExtension):
    forms = None

    def __init__(self, factory):
        super(FormExtension, self).__init__(factory)

        self.forms = {}

    def get_metadata(self, model_name):
        if not model_name in self.forms:
            self.forms[model_name] = FormMetadata()
        return self.forms[model_name]

class Mist(object):
    pass

class FormMetadata(FixtureMetadata):
    form = None

    def __init__(self):
        self.form = forms.Form()

    def convert(self, data):
        form = self.form

        # Convert groups to fields and their params
        for name, params in data.items():
            values = []
            for field_args in params:
                field_name = field_args[0]
                field_args[0] = form[field_name]

                # convert dict to object
                if len(field_args) > 1:
                    for i, field_arg in enumerate(field_args[1:], 1):
                        field_value = Mist()
                        field_value.__dict__ = field_arg
                        field_args[i] = field_value
                    values.append(field_args)
                else:
                    values.append(field_args[0])
            setattr(form, name, values)
        return form

    def update(self, descriptor):
        for field_name, field_params in descriptor.items():
            type = field_params.get('type', 'text')
            if 'type' in field_params:
                del field_params['type']

            fields_constructor = FIELDS.get(type, 'text')
            field = fields_constructor(**field_params)
            self.form.fields[field_name] = field
