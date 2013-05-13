# -*- coding: utf-8 -*-

from django.db import models
from clever.deferred.base import DeferredConsumer
from clever.deferred.base import DeferredMetaclass


class DeferredForeignKey(DeferredConsumer):
    def __init__(self, point, *args, **kwargs):
        super(DeferredForeignKey, self).__init__(point)

        self.fk_args = args
        self.fk_kwargs = kwargs

    def resolve_deferred_point(self, target_model):
        if not self.consumer_name:
            raise RuntimeError('DeferredForeignKey не является значением')

        # Создание реального первичного ключа
        foreign_key = models.ForeignKey(target_model, *self.fk_args, **self.fk_kwargs)
        self.consumer_model.add_to_class(self.consumer_name, foreign_key)


class DeferredModelMetaclass(DeferredMetaclass, models.base.ModelBase):
    ''' Строчка для подготовки магии отложенных ключей '''
    pass
