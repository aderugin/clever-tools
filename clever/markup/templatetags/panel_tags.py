from django import template


register = template.Library()

@register.filter
def model_fields(model):
    return model._meta.fields

@register.filter
def model_verbose_name(model):
    return model._meta.verbose_name.title()
