# -*- coding: utf-8 -*-
from clever.catalog.models import Product

RECENTLY_SESSION_NAME = 'clever:recently_viewed'


class RecentlyViewed(object):
    kwargs = None
    request = None

    def __init__(self):
        self.items = []

    def add(self, id):
        self.items = self.items
        if (id in self.items):
            self.items.remove(id)
        self.items.append(id)

    def get_objects(self):
        if len(self.items) > 0:
            return Product.objects.filter(id__in=self.items)
        return []

    def get_ordered_objects(self):
        list = self.items
        objects = self.get_objects()
        ordered = []
        for element in list:
            for object in objects:
                if element == object.id:
                    ordered.append(object)
        ordered.reverse()
        return ordered

    @classmethod
    def load(cls, request):
        ''' Загрузка корзины из сессии '''
        return request.session.get(RECENTLY_SESSION_NAME, None) or cls()

    def save(self, request):
        ''' Сохранение корзины в сессии '''
        request.session[RECENTLY_SESSION_NAME] = self
