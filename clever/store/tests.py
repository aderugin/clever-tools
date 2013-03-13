# -*- coding: utf-8 -*-
import unittest
from .signals import order_submited
from django_any import any_model
from django.db.models import get_model
from rikitavi.apps.notifier.models import Notification, Template
from django.core import mail


class OrderTestCase(unittest.TestCase):

    def setUp(self):

        Notification.objects.all().delete()
        self.notification = any_model(
            Notification, slug="new_order")

        self.template = any_model(
            Template,
            active=True,
            notification=self.notification,
            subject='order_number #ORDER_NUMBER#',
            message='order_number #ORDER_NUMBER# <br />#PRODUCTS#'
        )

    def test_mail_send_after_submited(self):

        order_cls = get_model('store', 'Order')
        order_item_cls = get_model('store', 'OrderItem')

        offer_cls = get_model('catalog', 'item')
        product_cls = get_model('catalog', 'product')

        product = any_model(product_cls, section=None, brand=None, image=None)
        offer_1 = any_model(offer_cls, image=None, product=product, price=1000)

        order = any_model(order_cls)
        order_item = any_model(order_item_cls, catalog_item=offer_1, order=order)

        order_submited.send(sender=self, order=order)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, u'order_number %d' % order.id)
