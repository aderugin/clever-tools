# -*- coding: utf-8 -*-
"""
:mod:`clever.catalog.types.string` -- Модуль для работы со строковым типом данных
                                      свойств товаров
===================================

В данном модуле хранится данные для работы со строковым типом данных.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
"""

from django.db import models


class StringType:
    #def propogate_to_model(model):
    #    model.add_to_class('string_value', models.CharField())

    def get_value(self, product_attribute):
        return product_attribute.string_value

    def set_value(self, product_attribute, value):
        product_attribute.string_value = value

    def format_value(self, value):
        return unicode(value)
