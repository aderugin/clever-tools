from django import template
from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse, resolve

register = template.Library()

@register.inclusion_tag('private/d-catalog-sidebar.html')
def catalog_sidebar(metadata):

    return {

    }
