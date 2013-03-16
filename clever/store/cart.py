# -*- coding: utf-8 -*-
import decimal


class ItemBase(object):
    '''
    A shopping cart system for Ecommerce in Django.
    '''
    def __init__(self, itemid, product, quantity=1):
        self.itemid = itemid
        self.product = product
        self.quantity = quantity
        self.sale = 0

    @property
    def price(self):
        """ Цена товара / Если есть скидка она учитывается """
        if self.sale:
            return self.product.price - self.product.price * self.sale / 100
        return self.product.price

    @property
    def total_price(self):
        """ Цена умноженная на количество в корзине"""
        return self.price * self.quantity

    @property
    def total_price_wosale(self):
        """ Цена умноженная на количество в корзине """
        return self.product.price * self.quantity


class CartBase(object):
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

    def add_item(self, product, quantity=1):
        # Пытаемся найти товар в корзине
        ext_item = filter(lambda x: x.product.id == int(product.id), self.items)

        if ext_item:
            # если нашли это будет list поэтому стучим по индексу 0
            ext_item[0].quantity += quantity
        else:
            item = Item(self.next_item_id, product, quantity)
            self.items.append(item)


    def update_item_quantity(self, itemid, quantity):
        """ Изменяет количество товара в корзине
            :itemid: Ид элемента в корзине
            :quantity: Значение
        """
        quantity = int(quantity)

        ext_item = filter(lambda x: x.itemid == int(itemid), self.items)
        ext_item[0].quantity = quantity

        return {
            'new_quantity' : ext_item[0].quantity,
            'new_cost' : float(ext_item[0].product.price) * ext_item[0].quantity
        }

    def is_empty(self):
        return self.items == []


    def clear(self):
        self.items = list()


    def remove_item(self, itemid):
        self.items = filter(lambda x: x.itemid != int(itemid), self.items)

    def __iter__(self):
        return self.forward()

    def forward(self):
        current_index = 0
        while (current_index < len(self.items)):
            item = self.items[current_index]
            current_index += 1
            yield item

    def get_total_cost(self):
        '''  Возвращает общую сумму корзины '''

        cost = 0
        for item in self.items:
            cost += item.product.price * item.quantity

        return float(cost)

    def get_discount(self):
        """Сумма скидки от акций и от суммы заказа"""
        sale_ammount = float(self.sale_ammount)
        total = self.get_total_cost() - sale_ammount

        return_discount = None
        for discount in self.discounts:
            if (discount.active):
                return_discount = discount.value

        if (return_discount):
            return float(((total / 100) * return_discount) + sale_ammount)
        else:
            return sale_ammount

    def total_cost_with_sale(self):
        """Общая сумма с учетом скидки"""
        return self.get_total_cost() - self.get_discount()

    def get_count_items(self):
        if len(self.items):
            return reduce(lambda res, x: res + x.quantity, self.items, 0)
        else:
            return 0


def get_user_cart(request):
    return request.session.get('cart', None) or Cart()

