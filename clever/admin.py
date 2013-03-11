"""Admin classes for clever application."""

from django.contrib import admin

from clever.models import Example


class ExampleAdmin(admin.ModelAdmin):
    """Admin class for Example model class."""
    pass


admin.site.register(Example, ExampleAdmin)
