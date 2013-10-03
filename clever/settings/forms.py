# -*- coding: utf-8 -*-
from django import forms
from django.contrib.admin import helpers


def create_form(model):
    modelName = model  # What the FUCK??? It's Python, not PHP, but shit...

    class SettingsFormBase(forms.ModelForm):
        class Meta:
            model = modelName
    return SettingsFormBase
