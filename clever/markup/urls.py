from django.conf.urls import patterns, url, include
from clever.markup import views

def make_base_urls():
    return [
        url(r'^$', views.IndexView.as_view(), name='index'),
        url(r'^(?P<id>[^/]*)\.html$', views.PageView.as_view(), name='page'),
    ]

def make_markup_urls():
    return [
        url(r'^markup/', include((make_base_urls(), None, 'markup'))),
    ]
