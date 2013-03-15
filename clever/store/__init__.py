# -*- coding: utf-8 -*-
from .signals import order_submited
from django.dispatch import receiver
#from rikitavi.apps.notifier.models import Notification
from django.template import loader, Context


@receiver(order_submited)
def send_mail_after_order_submited(sender, **kwargs):
    """
    Send notification to user and admin when order submited
    """
    order = kwargs.get('order')
    t = loader.get_template('mail/products_table.html')
    c = Context({'order': order})
    products_html = t.render(c)

    variables = {
        'ORDER_NUMBER': str(order.id),
        'USER_EMAIL': order.user_email if order.user_email else u'Заказ без регистрации',
        'PRODUCTS': products_html
    }

    Notification.send('new_order', variables)
