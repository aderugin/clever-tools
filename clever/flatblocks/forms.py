# -*- coding: utf-8 -*-
from flatblocks.forms import FlatBlockForm as FlatBlockFormBase
from django import forms
from ckeditor.widgets import CKEditorWidget


class FlatBlockForm(FlatBlockFormBase):
    content = forms.CharField(
        widget=CKEditorWidget(config_name='default'),
        required=False
    )
