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
@AttributeManager.register_type(tag='float', verbose_name='Дробное число')
class FloatType(AttributeType):
    def create_field(self):
        return models.FloatField(blank=True, null=True)

    @property
    def is_range(self):
        return True

    def filter_value(self, value):
        '''
        Преобразовать строку в соответствующие значение Python
        '''
        try:
            if value is None or value == '' or value == u'':
                return None
            if isinstance(value, unicode):
                value = unicode.replace(value, u',', u'.')
            elif isinstance(value, str):
                value = str.replace(value, ',', '.')
            return float(value)
        except ValueError as e:
            return 0.0
        except TypeError as e:
            return 0.0
