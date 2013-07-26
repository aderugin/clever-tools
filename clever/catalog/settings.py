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

# Настройка списка разрешенных аттрибутов
CLEVER_ATTRIBUTES = getattr(settings, 'CLEVER_ATTRIBUTES', [
    'price'
])

# Настройка списка разрешенных типов аттрибутов
CLEVER_ATTRIBUTES_TYPES = getattr(settings, 'CLEVER_ATTRIBUTES_TYPES', [
    'string'
])

# Настройка списка разрешенных элементов управления аттрибутов
CLEVER_ATTRIBUTES_CONTROLS = getattr(settings, 'CLEVER_ATTRIBUTES_CONTROLS', [
    'checkbox',
    'select'
])

# Настройка класса для недавно просмотренных товаров
CLEVER_RECENTLY_VIEWED = getattr(settings, 'CLEVER_RECENTLY_VIEWED', 'clever.catalog.recently_viewed.RecentlyViewed')

# Настройка списка разрешенных аттрибутов
CLEVER_BRAND_REQUIRED = getattr(settings, 'CLEVER_BRAND_REQUIRED', True)
