# -*- coding: utf-8 -*-

from django.db import models
from clever.deferred.base import DeferredMetaclass


# ------------------------------------------------------------------------------
class DeferredModelMetaclass(DeferredMetaclass):
    ''' Строчка для подготовки магии отложенных ключей '''
    @classmethod
    def for_consumer(self, *bases):
        bases += (models.base.ModelBase,)
        return super(DeferredModelMetaclass, self).for_consumer(*bases)

    @classmethod
    def for_point(self, point, *bases):
        bases += (models.base.ModelBase,)
        return super(DeferredModelMetaclass, self).for_point(point, *bases)
