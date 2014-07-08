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
CLEVER_DYNAMIC_SETTINGS = {
    'BATCH_PROCESSING': False
}
CLEVER_DYNAMIC_SETTINGS.update(getattr(settings, 'CLEVER_DYNAMIC_SETTINGS', {}))