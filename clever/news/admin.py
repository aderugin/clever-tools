from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from clever.core.admin import AdminMixin
from clever.core.admin import thumbnail_column
from clever.seo.admin import inject_seo_inline


# ------------------------------------------------------------------------------
class SectionForm(forms.ModelForm):
    class Meta:
        widgets = {
            'text': CKEditorWidget(config_name='default')
        }


# ------------------------------------------------------------------------------
@inject_seo_inline()
class SectionAdmin(AdminMixin, admin.ModelAdmin):
    form = SectionForm


# ------------------------------------------------------------------------------
class NewsForm(forms.ModelForm):
    class Meta:
        widgets = {
            'text': CKEditorWidget(config_name='default')
        }


# ------------------------------------------------------------------------------
@inject_seo_inline()
class NewsAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ['active', 'admin_thumbnail', 'title', 'publish_at', 'created_at']
    list_display_links = ['admin_thumbnail', 'title']
    form = NewsForm

    @thumbnail_column(size='106x80')
    def admin_thumbnail(self, inst):
        return [inst.image]
