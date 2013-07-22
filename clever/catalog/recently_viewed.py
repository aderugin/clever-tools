# -*- coding: utf-8 -*-
from clever.catalog.models import Product

RECENTLY_SESSION_NAME = 'clever:recently_viewed'


class RecentlyViewed(object):
    kwargs = None
    request = None

    def __init__(self):
        self.items = []
        self.exclude = []

    def add(self, id):
        self.items = self.items
        if (id in self.items):
            self.items.remove(id)
        self.items.append(id)

    def get_objects(self):
        if len(self.items) > 0:
            return Product.objects.filter(id__in=self.items).exclude(id__in=self.exclude)
        return Product.objects.none()

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

    def add_exclude(self, id):
        self.exclude.append(id)

    @classmethod
    def load(cls, request):
        ''' Загрузка корзины из сессии '''
        recently_viewed = request.session.get(RECENTLY_SESSION_NAME, None) or cls()
        recently_viewed.exclude = []
        return recently_viewed

    def save(self, request):
        ''' Сохранение корзины в сессии '''
        request.session[RECENTLY_SESSION_NAME] = self
