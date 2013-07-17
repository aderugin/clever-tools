from django.contrib import admin
from .forms import FlatBlockForm
from flatblocks.admin import FlatBlockAdmin as FlatBlockAdminBase
from flatblocks.models import FlatBlock
from django.db import models
from django import forms
from ckeditor.widgets import CKEditorWidget

class FlatBlockAdmin(admin.ModelAdmin):
    formfield_overrides = {
            models.TextField: {'widget': CKEditorWidget(config_name='default')}
        }

admin.site.unregister(FlatBlock)
admin.site.register(FlatBlock, FlatBlockAdmin)
