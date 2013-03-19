# -*- coding: utf-8 -*-
import decimal
from decimal import Decimal

class ItemBase(object):
    '''
    A shopping cart system for Ecommerce in Django.
    '''
    def __init__(self, itemid, product, quantity=1):
        self.itemid = itemid
        self.product = product
        self.quantity = quantity

    #@property
    def price(self, **kwargs):
        """ Цена товара / Если есть скидка она учитывается """
        return self.product.price

    #@property
    def total_price(self, **kwargs):
        """ Цена умноженная на количество в корзине"""
        return self.price(**kwargs) * self.quantity


class CartBase(object):
    model = ItemBase

    def __init__(self):
        self.items = list()
        self.unique_item_id = 0
        self.action = None
        self.sale_ammount = 0
        self.gift = None
        self.discounts = []

    def _get_next_item_id(self):
        self.unique_item_id += 1
        return self.unique_item_id
    next_item_id = property(_get_next_item_id)

    def add_product(self, product, quantity=1):
        # Пытаемся найти товар в корзине
        ext_item = filter(lambda x: x.product.id == int(product.id), self.items)

        if ext_item:
            # если нашли это будет list поэтому стучим по индексу 0
            ext_item[0].quantity += quantity
        else:
            item = self.model(self.next_item_id, product, quantity)
            self.items.append(item)

    def find_product(self, product):
        '''Поиск товара в корзине'''
        ext_item = filter(lambda x: x.product.id == int(product.id), self.items)

        if ext_item:
            return ext_item[0]
        else:
            None


    def update_item_quantity(self, product, quantity):
        """ Изменяет количество товара в корзине
            :itemid: Ид элемента в корзине
            :quantity: Значение
        """
        quantity = int(quantity)

        ext_item = filter(lambda x: x.product.id == product.id, self.items)
        ext_item[0].quantity = quantity


    def is_empty(self):
        return self.items == []


    def clear(self):
        self.items = list()


    def remove_product(self, product):
        self.items = filter(lambda x: x.product.id != product.id, self.items)

    def __iter__(self):
        return self.forward()

    def forward(self):
        current_index = 0
        while (current_index < len(self.items)):
            item = self.items[current_index]
            current_index += 1
            yield item

    def get_total_cost(self, **kwargs):
        '''  Возвращает общую сумму корзины '''

        cost = 0
        for item in self.items:
            cost += item.total_price(**kwargs)

        return cost

    def get_count_items(self):
        if len(self.items):
            return reduce(lambda res, x: res + x.quantity, self.items, 0)
        else:
            return 0


def get_user_cart(request):
    return request.session.get('cart', None) or Cart()

