# # -*- coding: utf-8 -*-

# from haystack.indexes import *
# from models import Page


# class PageIndex(SearchIndex, Indexable):
#     """Поисковой индекс по страницам"""
#     active = BooleanField(model_attr='active')
#     text = CharField(document=True, use_template=True)
#     title = CharField(model_attr='title')
#     updated_at = DateTimeField(model_attr='updated_at')

#     def get_model(self):
#         return Page

#     def index_queryset(self, *args, **kwargs):
#         """Используется, когда весь индекс для модели обновляется."""
#         return Page.objects.select_related().all()
