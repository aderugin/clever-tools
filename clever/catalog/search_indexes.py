# -*- coding: utf-8 -*-

from haystack.indexes import *
from celery_haystack.indexes import CelerySearchIndex
from models import Product


class ProductIndex(CelerySearchIndex, Indexable):
    """Поисковой индекс по страницам"""
    active = BooleanField(model_attr='active')
    text = CharField(document=True, use_template=True)
    title = CharField(model_attr='title')
    price = FloatField(model_attr='price')
    updated_at = DateTimeField(model_attr='updated_at')

    def get_model(self):
        return Product.get_deferred_instance()

    def index_queryset(self, *args, **kwargs):
        """Используется, когда весь индекс для модели обновляется."""
        return Product.objects.select_related().all()
