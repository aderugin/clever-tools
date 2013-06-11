# -*- coding: utf-8 -*-
"""
:mod:`clever.magic` -- Методы для скрытия магии работы с моделями Django
===================================

В данном модуле хранится базовый набор моделей для работы с каталогом.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
"""

from django.db import models

def get_model_fields(model):
    """Получение полей из модели Django ORM"""
    return model._meta.fields


def get_related_objects(model):
    """Получение зависимых объектов из модели Django ORM"""
    return model._meta.get_all_related_objects()


def is_concrete_model(bases, dct):
    """Проверка абстрактности модели или её предков"""
    if models.Model in bases:
        return False
    # Проверка метаданных Django ORM
    meta = dct.get('Meta', None)
    if not meta:
        return True
    return not getattr(meta, 'abstract', False)


def get_meta_param(dct, name, error_message="Параметр не найден в метаданных"):
    """Получение параметра из метаданных джанго и последующее его удаление"""
    djmeta = dct.get('Meta', None)
    if not djmeta or not getattr(djmeta, name, None):
        raise RuntimeError(error_message)
    value = getattr(djmeta, name)
    delattr(djmeta, name)
    return value


def field(field_name, error_message="Параметр не найден в метаданных"):
    """
    Декоратор для определения класса модели и передачи в функцию обратного вызова для
    создания внешнего ключа на эту модель

    Функция обратного вызова:
        meta - Метакласс используемый для создания текущего класса
        model - Модель определенная для  внешнего ключа

    Возвращаемое значение функции обратного вызова:
        Кортеж с название и объектом поля в модели Django ORM

    Аргументы
        field_name - Название
        error_message -
    """
    def prepare(func):
        def wrapper(meta, model_name, bases, dct):
            ermessage = error_message % model_name
            model = get_meta_param(dct, field_name, error_message=ermessage)
            name, field = func(meta, model)
            dct.update({name: field})
        wrapper.is_before = True
        return wrapper
    return prepare


class ModelMetaclass(models.base.ModelBase):
    """Базовый метакласс для добавления полей и методов на основе метаданных"""
    def __new__(meta, name, bases, dct):
        if is_concrete_model(bases, dct):
            before_list = []
            after_list = []

            # Prepare events
            for fname in dir(meta):
                item = getattr(meta, fname, None)
                if getattr(item, 'is_before', False):
                    before_list.append(item)
                elif getattr(item, 'is_after', False):
                    after_list.append(item)

            # Trigger before events
            for i in before_list:
                i(name, bases, dct)

            # Create class
            model = super(ModelMetaclass, meta).__new__(meta, name, bases, dct)

            # Trigger after events
            for i in after_list:
                i(model)
        else:
            model = super(ModelMetaclass, meta).__new__(meta, name, bases, dct)
        return model
