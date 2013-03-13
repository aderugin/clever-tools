from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('rikitavi.apps.store.views',
    url(r'^add/(?P<item_id>[-\d]+)/$', 'add', name='store_add_to_cart'),
    url(r'^add/$', 'add', name='form_store_add_to_cart'),
    url(r'^add_items/$', 'add_items', name='form_store_add_items_to_cart'),
    #url(r'^cart/a/(?P<item_slug>[-\w]+)/$', 'buy', name='store_buy'),
    url(r'^cart/clear/$', 'clear_cart', name='store_clear_cart'),
    url(r'^cart/del/(?P<cart_item_id>[-\d]+)/', 'remove_from_cart', name='remove_from_cart'),
    url(r'^ajax_update/', 'update_cart_item', name='ajax_update'),
    url(r'^ajax/delivery_date/', AjaxDeliveryDate.as_view(), name='ajax_delivery_date'),
    url(r'^modal/nologin/$', CartModalNologin.as_view(), name='store_modal_nologin'),
    url(r'^modal/check/$', CartModalCheck.as_view(), name='store_modal_check'),
    url(r'^modal/checkout/$', CartModalCheckout.as_view(), name='store_modal_checkout'),
    url(r'^result/$', RobokassaResult.as_view(), name='store_robokassa_result'),
    url(r'', CartIndex.as_view(), name='store_cart')
)
