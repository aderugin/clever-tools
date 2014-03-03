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
    'text': create_field(forms.CharField),
    'textarea': create_field(forms.CharField, widget=forms.Textarea),
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
            self.forms[model_name] = FormMetadata(self, model_name)
        return self.forms[model_name]


class FormMetadata(FixtureMetadata):
    form = None
    factory = None
    model_name = None

    def __init__(self, factory, model_name):
        self.factory = factory
        self.model_name = model_name
        self.form = forms.Form()

    def convert(self, data):
        form = self.form

        object_converter = self.factory.factory.object

        # Convert groups to fields and their params
        for name, params in data.items():
            converter = object_converter.get_metadata('%s-%s' % (self.model_name, name))
            if isinstance(params, (list, set)):
                value = []
                for item in params:
                    value.append(converter.convert(item))
            elif isinstance(params, dict):
                value = converter.convert(params)

            setattr(form, name, value)
        return form

    def update(self, descriptor):
        for field_name, field_params in descriptor.items():
            type = field_params.get('type', 'text')
            if 'type' in field_params:
                del field_params['type']

            fields_constructor = FIELDS.get(type, 'text')
            field = fields_constructor(**field_params)
            self.form.fields[field_name] = field
