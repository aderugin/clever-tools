#*- coding: utf-8 -*-
"""
:mod:`clever.seo.settings` -- Модуль для получение настроек приложения или
                                  замена на базовые значения
=====================================================================================

В данном модуле хранится данные для работы со строковым типом данных.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
.. moduleauthor:: Антон Вахмин <html.ru@gmail.com>
"""
from django.conf import settings

# Настройка опция по умолчанию для списка разрешенных элементов управления аттрибутов
CLEVER_SEO_CLASS = getattr(settings, 'CLEVER_SEO_CLASS', None)
if not CLEVER_SEO_CLASS:
    raise RuntimeError(u'Не задана модель для хранения SEO данных')
