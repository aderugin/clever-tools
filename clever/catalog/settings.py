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

# Настройки дополнительных полей для элемента управления в фильтре для производителей
CLEVER_BRAND_FIELDS = getattr(settings, 'CLEVER_BRAND_FIELDS', [])

# Настройка класса для недавно просмотренных товаров
CLEVER_RECENTLY_VIEWED = getattr(settings, 'CLEVER_RECENTLY_VIEWED', 'clever.catalog.recently_viewed.RecentlyViewed')

# Настройка опция по умолчанию для списка отсуствующих параметров
CLEVER_EMPTY_LABEL = getattr(settings, 'CLEVER_EMPTY_LABEL', u"----")

# Настройки для range control
CLEVER_FILTER_RANGE_MAX_ARGS = getattr(settings, 'CLEVER_FILTER_RANGE_MAX_ARGS', {'class': "b-filter__input", 'placeholder': "от"})
CLEVER_FILTER_RANGE_MIN_ARGS = getattr(settings, 'CLEVER_FILTER_RANGE_MIN_ARGS', {'class': "b-filter__input", 'placeholder': "до"})

# Настройки для price control
CLEVER_FILTER_PRICE_MAX_ARGS = getattr(settings, 'CLEVER_FILTER_PRICE_MAX_ARGS', CLEVER_FILTER_RANGE_MAX_ARGS)
CLEVER_FILTER_PRICE_MIN_ARGS = getattr(settings, 'CLEVER_FILTER_PRICE_MIN_ARGS', CLEVER_FILTER_RANGE_MIN_ARGS)

# # Настройки для checkbox
CLEVER_FILTER_CHECKBOX_TEMPLATE = getattr(settings, 'CLEVER_FILTER_CHECKBOX_TEMPLATE', 'catalog/blocks/input/checkbox.html')
CLEVER_FILTER_SELECT_TEMPLATE = getattr(settings, 'CLEVER_FILTER_SELECT_TEMPLATE', 'catalog/blocks/input/select.html')
CLEVER_FILTER_RADIO_TEMPLATE = getattr(settings, 'CLEVER_FILTER_RADIO_TEMPLATE', 'catalog/blocks/input/radio.html')
CLEVER_FILTER_RANGE_TEMPLATE = getattr(settings, 'CLEVER_FILTER_RANGE_TEMPLATE', 'catalog/blocks/input/range.html')
CLEVER_FILTER_PRICE_TEMPLATE = getattr(settings, 'CLEVER_FILTER_PRICE_TEMPLATE', 'catalog/blocks/input/price.html')
CLEVER_FILTER_BRAND_TEMPLATE = getattr(settings, 'CLEVER_FILTER_BRAND_TEMPLATE', 'catalog/blocks/input/brand.html')

# # Настройки для bradcrumbs
CLEVER_BREADCRUMBS_CATALOG_TITLE = getattr(settings, 'CLEVER_BREADCRUMBS_CATALOG_TITLE', u'Каталог')

CLEVER_BREADCRUMBS_BRANDS_TITLE = getattr(settings, 'CLEVER_BREADCRUMBS_BRANDS_TITLE', u'Производители')
