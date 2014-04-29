# -*- coding: utf-8 -*-
import itertools
from clever.magic import get_model_fullname, get_model_by_name
from decimal import Decimal
from . import signals


class ItemBase(object):
    """
    Базовый класс для отдельной записи в корзине
    """
    id = None
    product = None
    count = 0
    options = None

    def __init__(self, id, product, count=1, options=[]):
        self.id = id
        self.product = product
        self.count = count
        self.options = options

    @property
    def title(self):
        """ Получение имени для одной единицы товара """
        return self.product.title

    @property
    def price(self):
        """ Получение цены для одной единицы товара """
        return self.product.price

    @property
    def total_price(self):
        """ Получение цены для всех единиц товара """
        return self.price * self.count


class CartBase(object):
    """
    Базовый класс для корзины

    Аттрибуты класса:
        item_class - Класс объектов для хранения товара и его количества и вычисления различных цен

    Аттрибуты экземпляра класса:
        items - Список продуктов в корзине. (list<self.item_class>)
        is_save - Сохранить изменения корзины
    """
    item_class = ItemBase
    is_save = False

    def __init__(self, item_class):
        self.items = list()
        self.item_class = item_class

    @property
    def is_empty(self):
        """
        Проверка корзины на отсутствие товаров в ней
        """
        return not len(self.items)

    @property
    def price(self):
        """ Общая стоимость товаров корзине """
        return reduce(lambda price, item: price + item.price, self.items, Decimal(0.0))

    @property
    def count(self):
        """ Получение количества всех единиц товара в корзине"""
        if len(self.items):
            return reduce(lambda count, item: count + item.count, self.items, 0)
        else:
            return 0

    def make_item_id(self, product, options=[]):
        """
        Создание уникального идентификатора для элемента корзины
        """
        name = get_model_fullname(product)
        id = product.id

        # корректный UID
        if name:
            uid = u"%s.%d" % (name, id)
        else:
            uid = u"%d" % id

        # Если есть опции добавить их в UID
        options_uid = "-".join(options)
        if options_uid:
            return uid + '-' + options_uid
        else:
            return uid

    def get(self, product, options=[]):
        """
        Поиск товара в корзине

        Аргументы:
            product - Экземпляр модели Продукт

        Возвращаемое значение:
            Экземпляр унаследованный от класса ItemBase, либо None если товар
            не найден в корзине
        """
        uid = self.make_item_id(product, options)
        ext_item = filter(lambda item: item.id == uid, self.items)
        if ext_item:
            return ext_item[0]
        else:
            None

    def add(self, product, count=1, options=[]):
        """
        Добавление товара в корзину

        Аргументы:
            product - Экземпляр модели Продукт
            count - Количество единиц продукта, для добавления в корзину
        """
        # Пытаемся найти товар в корзине
        item = self.get(product, options)

        if item:
            item.count += count
            signals.update_item.send(self, cart=self, item=item)
        else:
            item = self.item_class(self.make_item_id(product, options), product, count=count, options=options)
            signals.add_item.send(self, cart=self, item=item)
            self.items.append(item)
            self.is_save = True

    def delete(self, id):
        self.items = filter(lambda item: item.id != id, self.items)
        self.is_save = True

    def cleanup(self):
        """
        Очистка в корзины от несуществующих товаров
        """
        products = (,)

        # сбор существующих элементов в корзине
        for content_type, items in itertools.groupby(self.items, lambda item: get_model_fullname(item.product)):
            # ищем соответсвующую модель
            model_class = get_model_by_name(content_type)
            if model_class:
                indexes, items = itertools.tee(items)

                # сбор существующих индексов
                indexes = map(lambda item: item.product.id, indexes)
                indexes = model_class.objects.filter(id__in=indexes).values_list('id', flat=True)

                # фильтрация существующих элементов в

                # products.append(filter(indexes))


        # content_types = filter()
        # products = Product.objects.filter(id__in=[item.product.id for item in self.items]).values_list('id')
        # products = sum(products, ())

        self.items = filter(lambda x: x.id in products, self.items)

    # def update_item_count(self, product, count):
    #     """
    #     Изменяет количество товара в корзине
    #
    #     Аргументы:
    #         product - Ид элемента в корзине
    #         count - Значение
    #     """
    #     count = int(count)
    #
    #     ext_item = filter(lambda x: x.product.id == product.id, self.items)
    #     ext_item[0].count = count

    # def clear(self):
    #     """ Очистка корзины """
    #     self.items = list()

    # def remove_product(self, product):
    #     """ Полное удаление из корзины """
    #     self.items = filter(lambda x: x.product.id != product.id, self.items)

    def __iter__(self):
        """ Получение итератора по элементам корзины """
        return iter(self.items)

    def __len__(self):
        """ Получение количества элементов в корзине """
        return len(self.items)

    def __nonzero__(self):
        return 0 != len(self.items)