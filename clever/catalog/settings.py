#*- coding: utf-8 -*-
"""
:mod:`clever.catalog.settings` -- Модуль для получение настроек приложения или
                                  замена на базовые значения
=====================================================================================

В данном модуле хранится данные для работы со строковым типом данных.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
.. moduleauthor:: Антон Вахмин <html.ru@gmail.com>
"""
from django.conf import settings

# Настройка опция по умолчанию для списка разрешенных аттрибутов
CLEVER_ATTRIBUTES = getattr(settings, 'CLEVER_ATTRIBUTES', [
    'price'
])

# Настройка опция по умолчанию для списка разрешенных типов аттрибутов
CLEVER_ATTRIBUTES_TYPES = getattr(settings, 'CLEVER_ATTRIBUTES_TYPES', [
    'string'
])

# Настройка опция по умолчанию для списка разрешенных элементов управления аттрибутов
CLEVER_ATTRIBUTES_CONTROLS = getattr(settings, 'CLEVER_ATTRIBUTES_CONTROLS', [
    'checkbox',
    'select'
])
