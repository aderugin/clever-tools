# -*- coding: utf-8 -*-
"""
:mod:`clever.catalog.models` -- Модели базового каталога
===================================

В данном модуле хранится базовый набор моделей для работы с каталогом.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
"""

from django.db import models
from caching import base as cache_machine
from clever.catalog.controls import SelectControl
from clever.catalog.controls import CheckboxControl
from clever.catalog.controls import RadioControl
from clever.catalog.controls import RangeControl
from clever.core.models import TimestableMixin
from clever.core.models import ActivableMixin
from clever.core.models import ActivableQuerySet
from clever.core.models import TitleMixin
from clever.core.models import TitleQuerySet
from clever.core.models import PageMixin
from clever.core.models import CachingPassThroughManager
from clever.core.models import TreeCachingPassThroughManager
from clever.core.models import extend_meta
from clever.deferred import DeferredPoint
from clever.deferred.fields import DeferredForeignKey
from clever.deferred.models import DeferredModelMetaclass
from mptt import models as mptt
from caching.base import CachingManager


# ------------------------------------------------------------------------------
Section = DeferredPoint('Section')

# ------------------------------------------------------------------------------
Brand = DeferredPoint('Brand')

# ------------------------------------------------------------------------------
Product = DeferredPoint('Product')

# ------------------------------------------------------------------------------
Attribute = DeferredPoint('Attribute')

# ------------------------------------------------------------------------------
ProductAttribute = DeferredPoint('ProductAttribute')

# ------------------------------------------------------------------------------
SectionAttribute = DeferredPoint('SectionAttribute')

# ------------------------------------------------------------------------------
SectionBrand = DeferredPoint('SectionBrand')

# ------------------------------------------------------------------------------
PseudoSection = DeferredPoint('PseudoSection')

# ------------------------------------------------------------------------------
PseudoSectionValue = DeferredPoint('PseudoSectionValue')

# ------------------------------------------------------------------------------
PseudoSectionBrand = DeferredPoint('PseudoSectionBrand')


# ------------------------------------------------------------------------------
# Разделы каталога
class SectionQuerySet(cache_machine.CachingQuerySet, ActivableQuerySet, TitleQuerySet):
    """Базовый запрос для получения продуктов из каталога"""

    def with_products(self):
        return self.annotate(products_count=models.Count('products')).filter(products_count__gt=0)


# ------------------------------------------------------------------------------
class SectionBase(cache_machine.CachingMixin, mptt.MPTTModel, TimestableMixin, ActivableMixin, TitleMixin, PageMixin):
    """Базовая модель для раздела в каталоге"""
    class Meta:
        abstract = True

    class MPTTMeta:
        parent_attr = "section"

    __metaclass__ = DeferredModelMetaclass.for_point(
        Section,
        extend_meta(
            verbose_name=u'Раздел',
            verbose_name_plural=u'Разделы'
        ),
        mptt.MPTTModelBase
    )

    section = mptt.TreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=u'Родительский раздел')

    code = models.CharField(verbose_name=u'Внутренний код', help_text=u'Код для связи с внешними сервисами, например 1C', max_length=50, blank=True)

    objects = TreeCachingPassThroughManager(SectionQuerySet)
    sections = TreeCachingPassThroughManager(SectionQuerySet)

    def __unicode__(self):
        return self.title

    @property
    def descendant_sections(self):
        ''' Получить queryset для подкатегорий '''
        return self.__class__.sections.filter(section=self)


# ------------------------------------------------------------------------------
# Производители(бренды) каталога
class BrandQuerySet(cache_machine.CachingQuerySet, ActivableQuerySet, TitleQuerySet):
    """Базовый запрос для получения продуктов из каталога"""
    def with_products(self):
        return self.annotate(products_count=models.Count('products')).filter(products_count__gt=0)


# ------------------------------------------------------------------------------
class BrandBase(cache_machine.CachingMixin, TimestableMixin, ActivableMixin, TitleMixin, PageMixin):
    """Базовая модель для производителя в каталоге"""
    class Meta:
        abstract = True

    __metaclass__ = DeferredModelMetaclass.for_point(
        Brand,
        extend_meta(
            verbose_name=u'Производитель',
            verbose_name_plural=u'Производители'
        )
    )

    code = models.CharField(verbose_name=u'Внутренний код', help_text=u'Код для связи с внешними сервисами, например 1C', max_length=50, blank=True)

    objects = CachingPassThroughManager(BrandQuerySet)
    brands = CachingPassThroughManager(BrandQuerySet)

    def __unicode__(self):
        return self.title

    @property
    def descendant_sections(self):
        ''' Получить queryset для категорий в которых есть продукт данного производителя '''
        return Section.sections.filter(products__brand=self).distinct()
        # context['section_list'] = self.get_sec(self.get_object())
        # return self.__class__.sections.filter(section=self)


# ------------------------------------------------------------------------------
class SectionBrandBase(cache_machine.CachingMixin, models.Model):
    """Базовая модель для настройки бренда в отдельном разделе"""
    class Meta:
        abstract = True

    __metaclass__ = DeferredModelMetaclass.for_point(
        SectionBrand,
        extend_meta(
            verbose_name=u'Параметры для производителя в разделе',
            verbose_name_plural=u'Параметры для производителей в разделе'
        )
    )

    section = DeferredForeignKey(Section, verbose_name=u'Раздел', null=False, blank=False)
    brand = DeferredForeignKey(Brand, verbose_name=u'Производитель', null=False, blank=False)
    order = models.IntegerField(verbose_name=u'Позиция', help_text=u'Расположение в фильтре', default=500)

    objects = CachingManager()


# ------------------------------------------------------------------------------
# Товары каталога
class ProductQuerySet(cache_machine.CachingQuerySet, ActivableQuerySet, TitleQuerySet):
    """Базовый запрос для получения продуктов из каталога"""


# ------------------------------------------------------------------------------
class ProductFrontendManager(CachingPassThroughManager):
    """Менеджер для получения только активных продуктов из каталога"""
    def get_query_set(self):
        return super(ProductFrontendManager, self).get_query_set().active()


# ------------------------------------------------------------------------------
class ProductBase(cache_machine.CachingMixin, TimestableMixin, ActivableMixin, TitleMixin, PageMixin):
    """Базовая модель для продукта в каталоге"""
    class Meta:
        abstract = True

    __metaclass__ = DeferredModelMetaclass.for_point(
        Product,
        extend_meta(
            verbose_name=u'Товар',
            verbose_name_plural=u'Товары'
        )
    )

    section = DeferredForeignKey(Section, verbose_name='Раздел', null=False, blank=False, related_name='products')
    brand = DeferredForeignKey(Brand, verbose_name='Раздел', null=False, blank=False, related_name='products')
    code = models.CharField(verbose_name=u'Внутренний код', help_text=u'Код для связи с внешними сервисами, например 1C', max_length=50, blank=True)

    objects = CachingPassThroughManager(ProductQuerySet)
    products = ProductFrontendManager(ProductQuerySet)

    def __unicode__(self):
        return self.title


# ------------------------------------------------------------------------------
# Аттрибуты(свойства) товаров каталога
class AbstractAttribute:
    ''' Промежуточный класс для работы с типами как классами '''
    @property
    def title(self):
        """ Получение заголовка """
        raise NotImplementedError

    @property
    def query_name(self):
        """ Получение имени в queryset """
        raise NotImplementedError

    @property
    def uid(self):
        """ Получение ID/имени в форме фильтра """
        raise NotImplementedError

    @property
    def control_object(self):
        ''' Получение контрола управления в форме фильтре '''
        raise NotImplementedError

    def make_query(self):
        ''' Создание начального фильтра в queryset '''
        return None

    def __unicode__(self):
        return self.title


# ------------------------------------------------------------------------------
class AttributeManager:
    # Элементы управления
    CONTROL_CHOICES = []
    CONTROL_CLASSES = {}
    ATTRIBUTES = []

    @classmethod
    def register_control(cls, control_cls):
        """ Регистрация нового элемента управления для аттрибута в форме фильтра """
        cls.CONTROL_CLASSES[control_cls.tag] = control_cls
        cls.CONTROL_CHOICES.append((control_cls.tag, control_cls.name))

    @classmethod
    def get_control(cls, control):
        if control in cls.CONTROL_CLASSES:
            return cls.CONTROL_CLASSES[control]()
        return cls.CONTROL_CLASSES['checkbox']()

    @classmethod
    def register_attribute(cls, attribute_cls):
        cls.ATTRIBUTES.append(attribute_cls)

    @classmethod
    def get_attributes(cls):
        return [attribute_cls() for attribute_cls in cls.ATTRIBUTES]


# Регистрация контролов в фильтре
AttributeManager.register_control(SelectControl)
AttributeManager.register_control(CheckboxControl)
AttributeManager.register_control(RadioControl)
AttributeManager.register_control(RangeControl)


# Регистрация псевдо свойств в фильтре
class BrandAttribute(AbstractAttribute):
    ''' Псевдо аттрибут для брэнда '''
    title = 'Производитель'
    control_object = CheckboxControl()
    query_name = 'brand'
    uid = 'brand'

    def get_values(self, section):
        return Brand.brands.filter(products__section=section).distinct().values_list('id', 'title')
AttributeManager.register_attribute(BrandAttribute)


# ------------------------------------------------------------------------------
class AttributeBase(cache_machine.CachingMixin, models.Model, AbstractAttribute):
    """Базовая модель для свойства"""
    class Meta:
        abstract = True

    __metaclass__ = DeferredModelMetaclass.for_point(
        Attribute,
        extend_meta(
            verbose_name=u'Свойство',
            verbose_name_plural=u'Свойства'
        )
    )

    code = models.CharField(verbose_name=u'Внутренний код', help_text=u'Код для связи с внешними сервисами, например 1C', max_length=50, blank=True)
    main_title = models.CharField(verbose_name=u'Заголовок', max_length=255)
    additional_title = models.CharField(verbose_name=u"Дополнительный заголовок", max_length=50, blank=True, null=True,
                                        help_text=u'Заполняется если нужно переопределить основной заголовок из 1С')

    is_filtered = models.BooleanField(verbose_name=u'Отображать в фильтре', default=True, blank=False, null=False)
    control = models.CharField(verbose_name=u'Элемент управления', help_text=u'для отображения в форме фильтра',
                               choices=AttributeManager.CONTROL_CHOICES, max_length=30, null=False, blank=False, default='select')

    objects = CachingManager()

    @property
    def title(self):
        """Получение заголовка"""
        if self.additional_title:
            return self.additional_title
        return self.main_title

    @property
    def uid(self):
        return 'attribute-' + str(self.id)

    @property
    def query_name(self):
        return 'attributes__string_value'

    def make_query(self):
        return models.Q(attributes__attribute=self)

    @property
    def control_object(self):
        """Получение стратегии для работы с элементом для отображения свойства в фильтре"""
        if getattr(self, '_control_object', None) is None:
            self._control_object = AttributeManager.get_control(self.control)
        return self._control_object

    def __unicode__(self):
        return self.title


# ------------------------------------------------------------------------------
class ProductAttributeBase(cache_machine.CachingMixin, models.Model):
    """Базовая модель для хранения значения свойства у продукта"""
    __metaclass__ = DeferredModelMetaclass.for_point(
        ProductAttribute,
        extend_meta(
            verbose_name=u'Значение свойства',
            verbose_name_plural=u'Значения свойства'
        )
    )

    class Meta:
        abstract = True

    product = DeferredForeignKey(Product, null=False, related_name='attributes')
    attribute = DeferredForeignKey(Attribute, null=False, related_name='values')

    string_value = models.CharField(verbose_name=u"Значение", max_length=255)
    objects = CachingManager()

    @property
    def value(self):
        return self.string_value

    @value.setter
    def value(self, value):
        self.string_value = value


# ------------------------------------------------------------------------------
class SectionAttributeBase(cache_machine.CachingMixin, models.Model):
    """Базовая модель для настройки свойства в отдельном разделе"""
    __metaclass__ = DeferredModelMetaclass.for_point(
        SectionAttribute,
        extend_meta(
            verbose_name=u'Параметры для свойства в разделе',
            verbose_name_plural=u'Параметры для свойств в разделе'
        )
    )

    class Meta:
        abstract = True

    section = DeferredForeignKey(Section, null=False)
    attribute = DeferredForeignKey(Attribute, null=False)
    order = models.IntegerField(verbose_name=u'Позиция', help_text=u'Расположение в фильтре', default=500)
    objects = CachingManager()


# ------------------------------------------------------------------------------
# Псевдо разделы каталога
class PseudoSectionQuerySet(cache_machine.CachingQuerySet, ActivableQuerySet, TitleQuerySet):
    """Базовый запрос для получения псевдо категорий из каталога"""


# ------------------------------------------------------------------------------
class PseudoSectionFrontendManager(CachingPassThroughManager):
    """Менеджер для получения только активных псевдо категорий из каталога"""
    def get_query_set(self):
        return super(PseudoSectionFrontendManager, self).get_query_set().active()


# ------------------------------------------------------------------------------
class PseudoSectionBase(cache_machine.CachingMixin, TitleMixin, TimestableMixin, ActivableMixin, PageMixin):
    """ Псевдо раздел каталога """
    class Meta:
        abstract = True

    __metaclass__ = DeferredModelMetaclass.for_point(
        PseudoSection,
        extend_meta(
            verbose_name=u'Псевдо раздел',
            verbose_name_plural=u'Псевдо разделы'
        )
    )

    section = DeferredForeignKey(Section, verbose_name=u'Раздел')
    objects = CachingPassThroughManager(PseudoSectionQuerySet)
    pseudo_sections = PseudoSectionFrontendManager(PseudoSectionQuerySet)

    def __unicode__(self):
        return ' '.join([self.section.title, ' > ', self.title])


# ------------------------------------------------------------------------------
class PseudoSectionValueBase(models.Model):
    """ Значение для фильтра псевдо-категории """
    __metaclass__ = DeferredModelMetaclass.for_point(
        PseudoSectionValue,
        extend_meta(
            verbose_name=u'Значение свойства в псевдо разделе',
            verbose_name_plural=u'Значения свойств в псевдо разделе'
        )
    )

    class Meta:
        abstract = True

    pseudo_section = DeferredForeignKey(PseudoSection, verbose_name=u'Псевдо раздел')
    attribute = DeferredForeignKey(Attribute, verbose_name=u'Свойство')
    string_value = models.CharField(verbose_name=u"Значение", max_length=255)


# ------------------------------------------------------------------------------
class PseudoSectionBrandBase(models.Model):
    """ Брэнды для фильтра псевдо-категории """
    __metaclass__ = DeferredModelMetaclass.for_point(
        PseudoSectionBrand,
        extend_meta(
            verbose_name=u'Значение производителя в псевдо разделе',
            verbose_name_plural=u'Значения производителя в псевдо разделе'
        )
    )

    class Meta:
        abstract = True

    pseudo_section = DeferredForeignKey(PseudoSection, verbose_name=u'Псевдо раздел')
    brand = DeferredForeignKey(Brand, verbose_name=u'Производитель', related_name='pseudo_section_brands')
