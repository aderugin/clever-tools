# -*- coding: utf-8 -*-

from clever.catalog.models import Product
from clever.catalog.models import ProductAttribute

def filter_view(view):
    views = ['all', 'main', 'diff']
    if view in views:
        return view
    return views[0]


class CompareStrategy():
    ''' Стратегия сравнения аттрибутов '''
    def compare(self, attribute, values):
        '''
            Данная функция должна вернуть True, для отображения аттрибута и
            его значения для продуктов раздела
        '''
        raise NotImplementedError()


class AllStrategy(CompareStrategy):
    ''' Показ всех свойств '''
    def compare(self, attribute, values):
        return True


class DifferentStrategy(CompareStrategy):
    ''' Показ только отличающехся свойств '''
    def compare(self, attribute, values):
        if len(values) > 1:
            # return all(lambda x: x != values[0], values)
            first = values[0]
            for second in values[1:]:
                if second is None and first is not None:
                    return True
                elif first is None and second is not None:
                    return True
                elif second.value != first.value:
                    return True
        return False


class CompareGroup:
    """
    Данная
    """
    section = None
    items = []

    def __init__(self, section):
        self.section = section
        self.items = []

    def add(self, product):
        self.items.append(product)

    def compare_attributes(self, strategy):
        indexes = [p.id for p in self.items]
        queryset = ProductAttribute.objects.all().filter(product__id__in=indexes).select_related('attribute', 'product')
        all_attributes = []
        all_values = {}

        # Фасовка значений по аттрибутам и продуктам
        for value in queryset:
            pid = value.product.id
            aid = value.attribute.id

            if not aid in all_values:
                all_attributes.append(value.attribute)
                all_values[aid] = {}
            all_values[aid][pid] = value

        # Привязываем значения аттрибутов продуктов к типам аттрибутов
        attributes = []
        for attribute in all_attributes:
            aid = attribute.id
            temp = []
            current = all_values[aid]

            # Поиск значений свойства для продуктов
            for product in self.items:
                pid = product.id
                if pid in current:
                    temp.append(current[pid])
                else:
                    temp.append(None)

            # Добавляем если нужно
            if strategy.compare(attribute, temp):
                attribute.compared_values = temp
                attributes.append(attribute)

        return attributes

    @property
    def id(self):
        return self.section.id

    @property
    def title(self):
        return self.section.title


class Comparer:
    """
    Модель для управления коллекцией сравниваемых
    """
    def __init__(self):
        self.items = set()

    @staticmethod
    def load(request):
        """
        Загрузка списка сравнения из сессии
        """
        return request.session.get('compare', None) or Comparer()

    def save(self, request):
        """
        Сохранить изминения списка сравнения в сессии
        """
        request.session['compare'] = self

    def add(self, id):
        """
        Добавить элемент в список сравнения
        """
        self.items.add(long(id))

    def remove(self, id):
        """
        Удалить элемент из списка сравнения
        """
        self.items.discard(long(id))

    def clear(self):
        self.items = set()

    def clear_group(self, id):
        for id in Product.objects.filter(section_id=id).values_list('id', flat=True):
            self.items.discard(long(id))

    def has(self, item):
        """
        Отмечен ли товар для сравнения
        """
        for group in self.get_groups():
            for child in group.items:
                if child and item and child.id == item.id:
                    return True
        return False

    def get_groups(self, view='all'):
        products = Product.objects.filter(id__in=self.items).select_related('section')
        groups = {}
        for p in products:
            section = p.section
            if not section.id in groups:
                groups[section.id] = CompareGroup(section)
            group = groups[section.id]
            group.add(p)

        temp = groups
        groups = []
        for group in temp.values():
            if len(group.items) > 0:
                groups.append(group)

        return groups

    def __iter__(self):
        groups = self.get_groups()
        return iter(groups)
