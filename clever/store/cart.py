# -*- coding: utf-8 -*-
CART_SESSION_NAME = 'cart'


# ------------------------------------------------------------------------------
class ItemBase(object):
    '''
    Базовый класс для отдельной записи в корзине
    '''

    def __init__(self, itemid, product, quantity=1):
        self.itemid = itemid
        self.product = product
        self.quantity = quantity

    @property
    def title(self):
        ''' Получение имени для одной единицы товара '''
        return self.product.title

    def get_price(self, **kwargs):
        ''' Вычисление цены отдельной единицы товара в корзине '''
        return self.product.price

    @property
    def price(self):
        ''' Получение цены для одной единицы товара '''
        return self.get_price()

    def get_total_price(self, **kwargs):
        ''' Вычисление полной цена для всех единиц товара в корзине '''
        return self.get_price(**kwargs) * self.quantity

    @property
    def total_price(self):
        ''' Получение цены для всех единиц товара '''
        return self.get_total_price()


# ------------------------------------------------------------------------------
class CartBase(object):
    '''
    Базовый класс для корзины

    Аттрибуты класса:
        item_model - Класс объектов для хранения товара и его количества и вычисления различных цен

    Аттрибуты экземпляра класса:
        items - Список продуктов в корзине. (list<self.item_model>)
    '''
    item_model = ItemBase

    def __init__(self):
        self.items = list()
        self.unique_item_id = 0

    @property
    def next_item_id(self):
        ''' Генерация новой идентификатора для записи в корзине '''
        self.unique_item_id += 1
        return self.unique_item_id

    def add_product(self, product, quantity=1):
        #TODO Сделать проверку данных quantity
        '''
        Добавление товара в корзину

        Аргументы:
            product - Экземпляр модели Продукт
            quantity - Количество единиц продукта, для добавления в корзину
        '''
        # Пытаемся найти товар в корзине
        ext_item = filter(lambda x: x.product.id == int(product.id), self.items)

        if ext_item:
            # если нашли это будет list поэтому стучим по индексу 0
            ext_item[0].quantity += quantity
        else:
            item = self.item_model(self.next_item_id, product, quantity)
            self.items.append(item)

    def find_product(self, product):
        '''
        Поиск товара в корзине

        Аргументы:
            product - Экземпляр модели Продукт

        Возвращаемое значение:
            Экземпляр унаследованный от класса ItemBase, либо None если товар
            не найден в корзине
        '''
        ext_item = filter(lambda x: x.product.id == int(product.id), self.items)

        if ext_item:
            return ext_item[0]
        else:
            None

    def update_item_quantity(self, product, quantity):
        '''
        Изменяет количество товара в корзине

        Аргументы:
            product - Ид элемента в корзине
            quantity - Значение
        '''
        quantity = int(quantity)

        ext_item = filter(lambda x: x.product.id == product.id, self.items)
        ext_item[0].quantity = quantity

    @property
    def is_empty(self):
        '''
        Проверка корзины на отсутствие товаров в ней

        TODO: Как сформулировать
        '''
        return len(self.items) == 0

    def clear(self):
        ''' Очистка корзины '''
        self.items = list()

    def remove_product(self, product):
        ''' Полное удаление из корзины '''
        self.items = filter(lambda x: x.product.id != product.id, self.items)

    def __iter__(self):
        ''' Получение итератора по элементам корзины '''
        return self.forward()

    def __len__(self):
        ''' Получение количества элементов в корзине '''
        return len(self.items)

    def forward(self):
        '''
        Реализация итератора для Python

        TODO: Проверить а надо ли нам это
        '''
        current_index = 0
        while (current_index < len(self.items)):
            item = self.items[current_index]
            current_index += 1
            yield item

    def get_total_price(self, **kwargs):
        '''  Возвращает общую стоимость корзины '''

        cost = 0
        for item in self.items:
            cost += item.get_total_price(**kwargs)

        return cost

    @property
    def total_price(self):
        ''' Общая стоимость товаров корзине '''
        return self.get_total_price()

    @property
    def count_items(self):
        ''' Получение количества единиц товара в корзине'''
        if len(self.items):
            return reduce(lambda res, x: res + x.quantity, self.items, 0)
        else:
            return 0

    @classmethod
    def load(cls, request):
        ''' Загрузка корзины из сессии '''
        return request.session.get(CART_SESSION_NAME, None) or cls()

    def save(self, request):
        ''' Сохранение корзины в сессии '''
        request.session[CART_SESSION_NAME] = self

    @classmethod
    def open(cls, request):
        ''' Загрузка корзины из сессии для использования с with '''
        return CartContext(request, cls)


# ------------------------------------------------------------------------------
class CartContext(object):
    def __init__(self, request, cls):
        self.request = request
        self.cls = cls
        self.cart = None

    def __enter__(self):
        if not self.cart:
            self.cart = self.cls.load(self.request)
        return self.cart

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            return False
        if self.cart and self.request:
            ''' Сохранение корзины в сессии '''
            self.cart.save(self.request)
        return True
