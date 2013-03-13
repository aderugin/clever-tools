# -*- coding: utf-8 -*-
# Author Semen Pupkov <semen.pupkov@gmail.com>
from .models import Delivery


class CalcDelivery(object):
    """Класс для расчета доставки"""

    def __init__(self, cart_cost):
        self.cart_total_cost = cart_cost
        
    def get_cost(self):
        
        delivery = Delivery.objects.filter(order_price_from__lte=self.cart_total_cost, order_price_to__gte=self.cart_total_cost)
        
        if delivery:
            return delivery[0].price
        else:
            return 0


