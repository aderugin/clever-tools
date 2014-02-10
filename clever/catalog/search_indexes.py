# # -*- coding: utf-8 -*-

# from haystack import indexes
# from celery_haystack.indexes import celery_indexes
# from models import Product


# class ProductIndex(celery_indexes.CelerySearchIndex, indexes.SearchIndex, indexes.Indexable):
#     """Поисковой индекс по страницам"""

#     active = BooleanField(model_attr='active')
#     text = CharField(document=True, use_template=True)
#     title = CharField(model_attr='title')
#     price = FloatField(model_attr='price')
#     updated_at = DateTimeField(model_attr='updated_at')

#     def get_model(self):
#         return Product.get_deferred_instance()

#     def index_queryset(self, *args, **kwargs):
#         """Используется, когда весь индекс для модели обновляется."""
#         return Product.objects.select_related().all()
