# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Page
from django import forms
from ckeditor.widgets import CKEditorWidget
from feincms.admin import editor
# from rollyourown.seo.admin import get_inline
# from rikitavi.seo import Metadata
from clever.seo.admin import inject_seo_inline

class PageAdminForm(forms.ModelForm):
    template = forms.ChoiceField(choices=Page.page_templates, widget=forms.Select)

    def __init__(self, *args, **kwargs):
        super(PageAdminForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget = CKEditorWidget(config_name='default')

@inject_seo_inline()
class PageAdmin(editor.TreeEditor):
    form = PageAdminForm
    list_display = ('title', 'slug', 'path', 'active', 'created_at', 'updated_at', )
    prepopulated_fields = {'slug': ('title',)}
    # inlines = [get_inline(Metadata)]

admin.site.register(Page, PageAdmin)
