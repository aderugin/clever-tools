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


# Настройка по умолчанию для таймаута кэша в фильтре
CLEVER_SETTINGS_TIMEOUT = getattr(settings, 'CLEVER_SETTINGS_TIMEOUT', 60*10)
