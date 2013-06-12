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
from decimal import Decimal


# ------------------------------------------------------------------------------
@AttributeManager.register_type(tag='price', verbose_name='Цена', allowed_only=True)
class PriceType(AttributeType):
    def create_field(self):
        return models.DecimalField(default=Decimal(0.00), decimal_places=2, max_digits=10)

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
            return Decimal(value)
        except ValueError as e:
            return Decimal(0.0)
        except TypeError as e:
            return Decimal(0.0)
