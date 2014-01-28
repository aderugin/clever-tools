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

# Настройка по умолчанию для списка разрешенных аттрибутов
CLEVER_ATTRIBUTES = getattr(settings, 'CLEVER_ATTRIBUTES', [
    'price'
])

# Настройка по умолчанию для списка разрешенных типов аттрибутов
CLEVER_ATTRIBUTES_TYPES = getattr(settings, 'CLEVER_ATTRIBUTES_TYPES', [
    'string'
])

# Настройка по умолчанию для списка разрешенных элементов управления аттрибутов
CLEVER_ATTRIBUTES_CONTROLS = getattr(settings, 'CLEVER_ATTRIBUTES_CONTROLS', [
    'checkbox',
    'select'
])

# Настройка по умолчанию для списка отсуствующих параметров
CLEVER_EMPTY_LABEL = getattr(settings, 'CLEVER_EMPTY_LABEL', u"----")

# Настройка по умолчанию для таймаута кэша в фильтре
CLEVER_FILTER_TIMEOUT = getattr(settings, 'CLEVER_FILTER_TIMEOUT', 60*10)
