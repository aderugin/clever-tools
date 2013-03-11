"""URLs for clever application."""

from django.conf.urls.defaults import *


urlpatterns = patterns('clever.views',
    url(r'^$', view='index', name='clever_index'),
)
