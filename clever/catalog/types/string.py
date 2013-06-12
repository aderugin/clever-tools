# -*- coding: utf-8 -*-
"""
:mod:`clever.catalog.types.string` -- Модуль для работы со строковым типом данных
                                      свойств товаров
===================================

В данном модуле хранится данные для работы со строковым типом данных.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
"""
from django.db import models
from clever.catalog.attributes import AttributeType
from clever.catalog.attributes import AttributeManager


# ------------------------------------------------------------------------------
@AttributeManager.register_type(tag='string', verbose_name='Строка', allowed_only=True)
class StringType(AttributeType):
    def create_field(self):
        return models.CharField(max_length=255, blank=True, null=True)

    def filter_value(self, value):
        '''
        Преобразовать строку в соответствующие значение Python
        '''
        return unicode(value)
