# -*- coding: utf-8 -*-
"""
:mod:`clever.catalog.models` -- Модели базового каталога
===================================

В данном модуле хранится базовый набор моделей для работы с каталогом.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
"""

from django.db import models
from caching import base as cache_machine
from clever.catalog.metaclass import ProductMetaclass
from clever.catalog.metaclass import ProductAttributeMetaclass
from clever.catalog.metaclass import SectionAttributeMetaclass
from clever.catalog.metaclass import SectionBrandMetaclass
from clever.core.models import generate_upload_name
from clever.core.models import TimestableMixin
from clever.core.models import ActivableMixin
from clever.core.models import ActivableQuerySet
from clever.core.models import TitleMixin
from clever.core.models import TitleQuerySet
from clever.core.models import PageMixin
from clever.core.models import CachingPassThroughManager
from mptt import models as mptt
from caching.base import CachingManager


class SectionQuerySet(cache_machine.CachingQuerySet, ActivableQuerySet, TitleQuerySet):
    """Базовый запрос для получения продуктов из каталога"""

    def with_products(self):
        return self.annotate(products_count=models.Count('products')).filter(products_count__gt=0)


class SectionFrontendManager(CachingPassThroughManager):
    """Менеджер для получения только активных продуктов из каталога"""
    def get_query_set(self):
        return super(SectionFrontendManager, self).get_query_set().active().with_products()


class SectionBase(cache_machine.CachingMixin, mptt.MPTTModel, TimestableMixin, ActivableMixin, TitleMixin, PageMixin):
    """Базовая модель для раздела в каталоге"""
    class Meta:
        abstract = True

    class MPTTMeta:
        parent_attr = "section"

    section = mptt.TreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=u'Родительский раздел')

    code = models.CharField(verbose_name=u'Внутренний код', help_text=u'Код для связи с внешними сервисами, например 1C', max_length=50, blank=True)

    objects = CachingPassThroughManager(SectionQuerySet)
    sections = SectionFrontendManager(SectionQuerySet)


class BrandQuerySet(cache_machine.CachingQuerySet, ActivableQuerySet, TitleQuerySet):
    """Базовый запрос для получения продуктов из каталога"""


class BrandFrontendManager(CachingPassThroughManager):
    """Менеджер для получения только активных продуктов из каталога"""
    def get_query_set(self):
        return super(BrandFrontendManager, self).get_query_set().active()


class BrandBase(cache_machine.CachingMixin, TimestableMixin, ActivableMixin, TitleMixin, PageMixin):
    """Базовая модель для производителя в каталоге"""
    class Meta:
        abstract = True

    code = models.CharField(verbose_name=u'Внутренний код', help_text=u'Код для связи с внешними сервисами, например 1C', max_length=50, blank=True)

    objects = CachingPassThroughManager(BrandQuerySet)
    brands = BrandFrontendManager(BrandQuerySet)


class ProductQuerySet(cache_machine.CachingQuerySet, ActivableQuerySet, TitleQuerySet):
    """Базовый запрос для получения продуктов из каталога"""


class ProductFrontendManager(CachingPassThroughManager):
    """Менеджер для получения только активных продуктов из каталога"""
    def get_query_set(self):
        return super(ProductFrontendManager, self).get_query_set().active()


class ProductBase(cache_machine.CachingMixin, TimestableMixin, ActivableMixin, TitleMixin, PageMixin):
    """Базовая модель для продукта в каталоге"""
    __metaclass__ = ProductMetaclass

    class Meta:
        abstract = True

    code = models.CharField(verbose_name=u'Внутренний код', help_text=u'Код для связи с внешними сервисами, например 1C', max_length=50, blank=True)

    objects = CachingPassThroughManager(ProductQuerySet)
    products = ProductFrontendManager(ProductQuerySet)


class AttributeType:
    """Стратегия для работы с отдельными свойствами"""
    def filter(self, queryset):
        """
        Фильтровать, используя данное свойство
        """
        pass

    def order_by(self, queryset, order="asc"):
        """
        Сортировать, используя данное свойство
        """
        pass


class AttributeStyle:
    """Стратегия для работы вывода отдельных свойств"""
    pass


class AttributeParams:
    """Пока что херь которая должна скрыть сложность получение данных для свойств с учетом категории"""
    def __init__(self, attribute, section_params):
        self.attribute = attribute
        self.section_params = list(section_params)

    def get_option(self, name, default=None):
        for param in self.section_params:
            value = getattr(param, name, None)
            if not value is None:
                return value
        return getattr(self.attribute, name, default)

    @property
    def is_filterable(self):
        return self.get_option('is_filterable')

    @property
    def is_primary(self):
        return self.get_option('is_primary')


class AttributeBase(cache_machine.CachingMixin, models.Model):
    """Базовая модель для свойства"""
    class Meta:
        abstract = True

    code = models.CharField(verbose_name=u'Внутренний код', help_text=u'Код для связи с внешними сервисами, например 1C', max_length=50, blank=True)
    main_title = models.CharField(verbose_name=u'Заголовок', max_length=255)
    additional_title = models.CharField(verbose_name=u"Дополнительный заголовок", max_length=50, blank=True, null=True,
        help_text=u'Заполняется если нужно переопределить основной заголовок из 1С')

    objects = CachingManager()

    @property
    def title(self):
        """Получение заголовка"""
        if self.additional_title:
            return self.additional_title
        return self.main_title

    @property
    def type_object(self):
        """Получение стратегии для работы с типом свойства"""
        from clever.catalog.types import StringType
        return StringType()

    @property
    def control_object(self):
        """Получение стратегии для работы с элементом для отображения свойства в фильтре"""
        from clever.catalog.controls import SelectControl
        return SelectControl()

    @property
    def is_filterable(self):
        """Главное свойство"""
        return True

    @property
    def is_primary(self):
        """Главное свойство"""
        return False

    def __unicode__(self):
        return self.title


class ProductAttributeBase(cache_machine.CachingMixin, models.Model):
    """Базовая модель для хранения значения свойства у продукта"""
    __metaclass__ = ProductAttributeMetaclass

    class Meta:
        abstract = True

    string_value = models.CharField(verbose_name=u"Значение", max_length=255)
    objects = CachingManager()

    @property
    def value(self):
        return self.string_value


class SectionAttributeBase(cache_machine.CachingMixin, models.Model):
    """Базовая модель для настройки свойства в отдельном разделе"""
    __metaclass__ = SectionAttributeMetaclass

    class Meta:
        abstract = True

    order = models.IntegerField(verbose_name=u'Позиция', help_text=u'Расположение в фильтре')
    objects = CachingManager()

    # in_filter = models.BooleanField('Показывать в фильтре', default=False)
    # in_main_props = models.BooleanField('Показывать в главных свойствах', default=False)
    # in_all_props = models.BooleanField('Показывать в свойствах товара', default=True)

    def is_filterable(self):
        """Главное свойство"""
        return True

    @property
    def is_primary(self):
        """Главное свойство"""
        return False


class SectionBrandBase(cache_machine.CachingMixin, models.Model):
    """Базовая модель для настройки бренда в отдельном разделе"""
    __metaclass__ = SectionBrandMetaclass

    class Meta:
        abstract = True

    order = models.IntegerField(verbose_name=u'Позиция', help_text=u'Расположение в фильтре')
    objects = CachingManager()


def register_attribute_type(cls):
    """Декоратор класса для регистрации нового типа аттрибута в каталоге"""
    pass


def register_attribute_style(cls):
    """Декоратор класса для регистрации нового стиля аттрибута в каталоге"""
    pass
