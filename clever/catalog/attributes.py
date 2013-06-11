#*- coding: utf-8 -*-
"""
:mod:`clever.catalog.attributes` -- Модуль для работы со числовым типом данных
                                    свойств товаров
================================================================================

В данном модуле хранится данные для работы со строковым типом данных.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
"""
from clever.magic import is_concrete_model
from django.db.models.signals import pre_save
from django.dispatch import receiver


# ------------------------------------------------------------------------------
class AbstractAttribute(object):
    ''' Промежуточный класс для работы с типами как классами '''
    @property
    def title(self):
        ''' Получение заголовка '''
        raise NotImplementedError()

    @property
    def query_name(self):
        ''' Получение имени в queryset '''
        raise NotImplementedError()

    @property
    def uid(self):
        ''' Получение ID/имени в форме фильтра '''
        raise NotImplementedError()

    @property
    def control_object(self):
        ''' Получение контрола управления в форме фильтре '''
        raise NotImplementedError()

    def make_query(self):
        ''' Создание начального фильтра в queryset '''
        return None

    def __unicode__(self):
        return self.title


# ------------------------------------------------------------------------------
class AttributeControl(object):
    '''
    Базовый класс для представлений(элементов управления) свойств в фильтре
    '''
    def __init__(self, tag, verbose_name):
        self.tag = tag
        self.verbose_name = verbose_name

    def create_form_field(self, attribute, values):
        '''
        Данный метод создает поле соответствуще представлению (элемент
        управления) свойства в форме фильтра
        '''
        raise NotImplementedError()

    def create_query_part(self, attribute, values):
        '''
        Данный метод создает часть запроса к Django ORM для фильтрования по
        данным свойства

        Для получение поля для хранения значения `attribute.query_name`

        '''
        raise NotImplementedError()

    def create_form_value(self, values):
        raise NotImplementedError()

    @property
    def is_range(self):
        return False


# ------------------------------------------------------------------------------
class AttributeType(object):
    '''
    Базовый класс для типов значений свойств
    '''
    def __init__(self, tag, verbose_name):
        super(AttributeType, self).__init__()

        self.tag = tag
        self.verbose_name = verbose_name

    def create_field(self):
        '''
        Получение отдельного поля или списка полей для значения свойства в продукте
        '''
        raise NotImplementedError()

    @property
    def is_range(self):
        '''
        Может ли данный тип использоваться в диапазонах значений?
        '''
        return False

    @property
    def field_name(self):
        '''
        Получение имен полей для хранения значения
        '''
        return self.tag + '_value'

    @property
    def range_names(self):
        '''
        Получение имен полей для хранения диапазона значений
        '''
        field_name = self.field_name
        if not self.is_range:
            return [field_name]
        return [field_name, field_name + '_to']

    def filter_value(self, value):
        '''
        Преоброзовать строку в соответствующие значение Python
        '''
        raise NotImplementedError()


# ------------------------------------------------------------------------------
class AttributeManager(object):
    '''
    Данный класс содержит информацию об свойствах товаров, их типах значений и
    представлений в фильтре каталога
    '''
    # Элементы управления
    CONTROLS_CHOICES = []
    CONTROLS_CLASSES = {}

    # Типы свойств
    TYPES_CHOICES = []
    TYPES_CLASSES = {}

    # Псевдо пользовательские аттрибуты
    PSEUDO_ATTRIBUTES = []

    @classmethod
    def get_control(cls, control):
        if control in cls.CONTROLS_CLASSES:
            return cls.CONTROLS_CLASSES[control]
        return cls.CONTROLS_CLASSES['checkbox']

    @classmethod
    def get_type(cls, type):
        if type in cls.TYPES_CLASSES:
            return cls.TYPES_CLASSES[type]
        return cls.TYPES_CLASSES['checkbox']

    @classmethod
    def get_attributes(cls):
        return [attribute_cls() for attribute_cls in cls.PSEUDO_ATTRIBUTES]

    @classmethod
    def get_types(cls):
        return cls.TYPES_CLASSES.items()

    @classmethod
    def register_attribute(cls, attribute_cls):
        cls.PSEUDO_ATTRIBUTES.append(attribute_cls)

    @classmethod
    def register_control(cls, tag, verbose_name):
        def outer_wrapper(control_cls):
            ''' Регистрация нового элемента управления для аттрибута в форме фильтра '''
            if tag in cls.CONTROLS_CLASSES:
                raise RuntimeError("Элемент управления свойства с тегом %s уже существует" % tag)

            control = control_cls(tag, verbose_name)
            cls.CONTROLS_CLASSES[tag] = control
            cls.CONTROLS_CHOICES.append((tag, verbose_name))
        return outer_wrapper

    @classmethod
    def register_type(cls, tag, verbose_name):
        '''
        Регистрация нового элемента управления для аттрибута в форме фильтра
        AttributeManager.register_type(tag='tag', verbose_name='Type name')
        '''
        def outer_wrapper(type_cls):
            if tag in cls.TYPES_CLASSES:
                raise RuntimeError("Тип свойства с тегом %s уже существует" % tag)

            type = type_cls(tag, verbose_name)
            cls.TYPES_CLASSES[tag] = type
            cls.TYPES_CHOICES.append((tag, verbose_name))
        return outer_wrapper


# ------------------------------------------------------------------------------
# Загружаем стандартные представления и типы для свойств
import clever.catalog.controls
import clever.catalog.types


# ------------------------------------------------------------------------------
class ImportProductAttributeValuesMetaclass(type):
    ''' Метк '''
    def __init__(meta, name, bases, attribs):
        super(ImportProductAttributeValuesMetaclass, meta).__init__(name, bases, attribs)

        if is_concrete_model(bases, attribs):
            fieldset = {}
            for type_name, type in AttributeManager.get_types():
                fieldset[type.field_name] = type.create_field()

            for field_name, field in fieldset.items():
                meta.add_to_class(field_name, field)


# ------------------------------------------------------------------------------
class ImportPseudoAttributeValuesMetaclass(type):
    ''' Метк '''
    def __init__(meta, name, bases, attribs):
        super(ImportPseudoAttributeValuesMetaclass, meta).__init__(name, bases, attribs)

        if is_concrete_model(bases, attribs):
            fieldset = {}
            for type_name, type in AttributeManager.get_types():
                if not type.is_range:
                    fieldset[type.field_name] = type.create_field()
                else:
                    fieldset[type.range_names[0]] = type.create_field()
                    fieldset[type.range_names[1]] = type.create_field()

            for field_name, field in fieldset.items():
                meta.add_to_class(field_name, field)
