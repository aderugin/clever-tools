# -*- coding: utf-8 -*-

from django.db import models
from clever import magic


# ------------------------------------------------------------------------------
# Инжекторы - части метаклассов ответственные за вставку ForeignKey's в модели
#             Django ORM
class SectionInjectMixin(type):
    @classmethod
    @magic.field('section_model', error_message="Для модели %s не указана модель категории")
    def add_section(cls, section_model):
        """Добавление ссылки на раздел"""
        return 'section', models.ForeignKey(section_model, verbose_name=u"Раздел", db_index=True, related_name=cls.related_name)


class BrandInjectMixin(type):
    @classmethod
    @magic.field('brand_model', error_message="Для модели %s не указана модель бренда")
    def add_brand(cls, brand_model):
        """Добавление ссылки на бренд"""
        return 'brand', models.ForeignKey(brand_model, verbose_name=u"Бренд", db_index=True, related_name=cls.related_name)


class AttributeInjectMixin(type):
    @classmethod
    @magic.field('attribute_model', error_message="Для модели %s не указана модель аттрибута")
    def add_attribute(cls, attribute_model):
        """Добавление ссылки на бренд"""
        return 'attribute', models.ForeignKey(attribute_model, verbose_name=u"Аттрибут", db_index=True, related_name=cls.related_name)


class ProductInjectMixin(type):
    @classmethod
    @magic.field('product_model', error_message="Для модели %s не указана модель продукта")
    def add_product(cls, product_model):
        """Добавление ссылки на бренд"""
        return 'product', models.ForeignKey(product_model, verbose_name=u"Продукт", db_index=True, related_name=cls.related_name)


class PseudoSectionInjectMixin(type):
    @classmethod
    @magic.field('pseudo_section_model', error_message="Для модели %s не указана модель категории")
    def add_section(cls, pseudo_section_model):
        """Добавление ссылки на раздел"""
        return 'pseudo_section', models.ForeignKey(pseudo_section_model, verbose_name=u"Раздел", db_index=True, related_name=cls.related_name)


# ------------------------------------------------------------------------------
# Метаклассы для создание реальных моделей каталога
class ProductMetaclass(magic.ModelMetaclass, SectionInjectMixin, BrandInjectMixin):
    """Метакласс для создания конкретной модели продукта"""
    related_name = 'products'


class ProductAttributeMetaclass(magic.ModelMetaclass, ProductInjectMixin, AttributeInjectMixin):
    """Метакласс для создания конкретной модели аттрибутов продукта"""
    related_name = 'attributes'


class SectionAttributeMetaclass(magic.ModelMetaclass, SectionInjectMixin, AttributeInjectMixin):
    """Метакласс для создания конкретной модели настроек аттрибутов для отдельного раздела"""
    related_name = 'attributes_params'


class SectionBrandMetaclass(magic.ModelMetaclass, SectionInjectMixin, BrandInjectMixin):
    """Метакласс для создания конкретной модели настроек бренда для отдельного раздела"""
    related_name = 'brand_params'


class PseudoSectionMetaclass(magic.ModelMetaclass, SectionInjectMixin):
    """ Метакласс для создания конкретной модели псевдо категорий """
    related_name = 'pseudo_sections'


class PseudoSectionValueMetaclass(magic.ModelMetaclass, PseudoSectionInjectMixin, AttributeInjectMixin):
    """ Метакласс для создания конкретной модели значение для свойства в фильтре """
    related_name = 'pseudo_section_values'


class PseudoSectionBrandMetaclass(magic.ModelMetaclass, PseudoSectionInjectMixin, BrandInjectMixin):
    """ Метакласс для создания конкретной модели значение для брэнда в фильтре """
    related_name = 'pseudo_section_brands'
