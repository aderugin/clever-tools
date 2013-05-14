from django.conf.urls import patterns, url
from .views import PageDetailView, HomePageView

urlpatterns = patterns('',
    url(r'^success/$', PageDetailView.as_view(), name='order_success'),
    url(r'^success-online/$', PageDetailView.as_view(), name='order_success_online'),
    url(r'^payment-success/$', PageDetailView.as_view(), name='order_success_payment'),
    url(r'^(?P<path>.*)/$', PageDetailView.as_view(), name='page'),
    url(r'^$', HomePageView.as_view(), name='homepage', kwargs={'slug': 'home'}),
)

