#*- coding: utf-8 -*-
"""
:mod:`clever.slider.settings` -- Модуль для получение настроек приложения или
                                  замена на базовые значения
=====================================================================================

В данном модуле хранится данные для работы со строковым типом данных.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
.. moduleauthor:: Антон Вахмин <html.ru@gmail.com>
"""
from django.conf import settings

CLEVER_SLIDER_HAS_EDIT = getattr(settings, 'CLEVER_SLIDER_HAS_EDIT', True)

CLEVER_SLIDER_HAS_DELETE = getattr(settings, 'CLEVER_SLIDER_HAS_DELETE', True)
