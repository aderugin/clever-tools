from django.conf.urls import patterns, url
from clever.markup import views

def make_markup_urls():
    return [
        url(r'^markup/$', views.IndexView.as_view(), name='index'),
        url(r'^markup/(?P<id>[^/]*)\.html$', views.PageView.as_view(), name='page'),
    ]
