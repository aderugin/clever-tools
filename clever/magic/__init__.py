# -*- coding: utf-8 -*-
"""
:mod:`clever.magic` -- Методы для скрытия магии работы с моделями Django
===================================

В данном модуле хранится базовый набор моделей для работы с каталогом.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
"""

from django.db import models
import importlib


def is_concrete_model(bases, dct):
    """Проверка абстрактности модели или её предков"""
    if models.Model in bases:
        return False
    # Проверка метаданных Django ORM
    meta = dct.get('Meta', None)
    if not meta:
        return True
    return not getattr(meta, 'abstract', False)


def load_class(cls):
    if not cls:
        raise ValueError(u'Пустое имя класса')

    module_name, class_name = cls.rsplit(".", 1)
    somemodule = importlib.import_module(module_name)
    clazz = getattr(somemodule, class_name)
    if not clazz:
        raise RuntimeError(u'Класс %s не найден' % cls)
    return clazz
