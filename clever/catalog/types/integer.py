# -*- coding: utf-8 -*-
"""
:mod:`clever.catalog.types.integer` -- Модуль для работы со числовым типом данных
                                      свойств товаров
===================================

В данном модуле хранится данные для работы со строковым типом данных.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
"""
from django.db import models
from clever.catalog.attributes import AttributeType
from clever.catalog.attributes import AttributeManager


# ------------------------------------------------------------------------------
@AttributeManager.register_type(tag='integer', verbose_name='Целое число', allowed_only=True)
class IntegerType(AttributeType):
    def create_field(self):
        return models.BigIntegerField(blank=True, null=True)

    @property
    def is_range(self):
        return True

    def filter_value(self, value):
        '''
        Преобразовать строку в соответствующие значение Python
        '''
        try:
            return long(value)
        except ValueError:
            return long(0)
        except TypeError:
            return long(0)
