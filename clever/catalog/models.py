# -*- coding: utf-8 -*-
"""
:mod:`clever.catalog.models` -- Модели базового каталога
===================================

В данном модуле хранится базовый набор моделей для работы с каталогом.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
"""
from clever.deferred import DeferredPoint

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
from django.db import models
from caching import base as cache_machine
from clever.deferred.fields import DeferredForeignKey
from clever.deferred.models import DeferredModelMetaclass
from clever.core.models import TimestableMixin
from clever.core.models import ActivableMixin
from clever.core.models import ActivableQuerySet
from clever.core.models import TitleMixin
from clever.core.models import TitleQuerySet
from clever.core.models import PageMixin
from clever.core.models import CachingPassThroughManager
from clever.core.models import TreeCachingPassThroughManager
from clever.core.models import extend_meta
from mptt import models as mptt
from caching.base import CachingManager
from clever.catalog.attributes import AbstractAttribute
from clever.catalog.attributes import AttributeManager
from clever.catalog.attributes import ImportProductAttributeValuesMetaclass
from clever.catalog.attributes import ImportPseudoAttributeValuesMetaclass
from decimal import Decimal


# ------------------------------------------------------------------------------
# Разделы каталога
class SectionQuerySet(cache_machine.CachingQuerySet, ActivableQuerySet, TitleQuerySet):
    """
        Базовый запрос для получения продуктов из каталога

        .. versionadded:: 0.1
    """

    def with_products(self):
        return self.filter(products__active=True).annotate(products_count=models.Count('products')).filter(products_count__gt=0)

    def with_ancestors(self):
        if isinstance(self, models.query.EmptyQuerySet):
            return self
        new_queryset = self.none()
        for obj in self:
            new_queryset = new_queryset | obj.get_ancestors()
        return new_queryset

    def with_descendants(self):
        if isinstance(self, models.query.EmptyQuerySet):
            return self
        new_queryset = self.none()
        for obj in self:
            new_queryset = new_queryset | obj.get_descendants()
        return new_queryset


# ------------------------------------------------------------------------------
class SectionBase(cache_machine.CachingMixin, mptt.MPTTModel, TimestableMixin, ActivableMixin, TitleMixin, PageMixin):
    """
        Базовая модель для раздела в каталоге

        .. note::
            Название url'а для обработки ``catalog:section`` с параметром ``slug``
            (ЧПУ раздела)

        .. versionadded:: 0.1
    """
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

    def __unicode__(self):
        return self.title

    @property
    def descendant_sections(self):
        '''
            Получить queryset для подкатегорий

            .. versionadded:: 0.1
        '''
        return self.__class__.objects.filter(section=self, active=True)

    @models.permalink
    def get_absolute_url(self):
        '''
        Получение URL'а для просмотра экземпляра модели

        .. versionadded:: 0.2
        '''
        return ('catalog:section', (), {'slug': self.slug})


# ------------------------------------------------------------------------------
# Производители(бренды) каталога
class BrandQuerySet(cache_machine.CachingQuerySet, ActivableQuerySet, TitleQuerySet):
    """Базовый запрос для получения продуктов из каталога"""
    def with_products(self):
        return self.annotate(products_count=models.Count('products')).filter(products_count__gt=0)


# ------------------------------------------------------------------------------
class BrandBase(cache_machine.CachingMixin, TimestableMixin, ActivableMixin, TitleMixin, PageMixin):
    """
        Базовая модель для производителя в каталоге

        .. note::
            Название url'а для обработки ``catalog:brand`` с параметром ``slug``
            (ЧПУ производителя)

        .. versionadded:: 0.1
    """
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

    def __unicode__(self):
        return self.title

    @property
    def descendant_sections(self):
        ''' Получить queryset для категорий в которых есть продукт данного производителя '''
        import pdb; pdb.set_trace()
        return Section.objects.filter(products__brand=self, active=True).distinct()

    @models.permalink
    def get_absolute_url(self):
        '''
        Получение URL'а для просмотра экземпляра модели

        .. versionadded:: 0.2
        '''
        return ('catalog:brand', (), {'slug': self.slug})


# ------------------------------------------------------------------------------
class SectionBrandBase(cache_machine.CachingMixin, models.Model):
    """Базовая модель для настройки бренда в отдельном разделе"""
    class Meta:
        abstract = True

    __metaclass__ = DeferredModelMetaclass.for_point(
        SectionBrand,
        extend_meta(
            verbose_name=u'Параметры для производителя в разделе',
            verbose_name_plural=u'Параметры для производителей в разделе',
            ordering=['order', 'brand__title', 'id']
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
    """
        Базовая модель для продукта в каталоге

        .. note::
            Название url'а для обработки ``catalog:product`` с параметром ``slug``
            (ЧПУ из продукта)

        .. versionadded:: 0.1
    """
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
    brand = DeferredForeignKey(Brand, verbose_name='Производитель', null=False, blank=False, related_name='products')
    code = models.CharField(verbose_name=u'Внутренний код', help_text=u'Код для связи с внешними сервисами, например 1C', max_length=50, blank=True)

    # Это новая цена
    price = models.DecimalField(verbose_name=u"Цена", default=Decimal(0.00), decimal_places=2, max_digits=10)

    objects = CachingPassThroughManager(ProductQuerySet)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        '''
        Получение URL'а для просмотра экземпляра модели

        .. versionadded:: 0.2
        '''
        return ('catalog:product', (), {'slug': self.slug})
    # url = property(get_absolute_url)


# ------------------------------------------------------------------------------
class AttributeBase(cache_machine.CachingMixin, models.Model, AbstractAttribute):
    """
        Базовая модель для свойства

        .. versionadded:: 0.1
    """
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

    type = models.CharField(verbose_name=u'Тип значения', help_text=u'для хранения и произведения операций',
                            choices=AttributeManager.TYPES_CHOICES, max_length=30, null=False, blank=False, default='string')
    control = models.CharField(verbose_name=u'Элемент управления', help_text=u'для отображения в форме фильтра',
                               choices=AttributeManager.CONTROLS_CHOICES, max_length=30, null=False, blank=False, default='select')

    objects = CachingManager()

    @property
    def title(self):
        """
            Получение заголовка

            .. versionadded:: 0.1
        """
        if self.additional_title:
            return self.additional_title
        return self.main_title

    @property
    def uid(self):
        return 'attribute-' + str(self.id)

    @property
    def query_name(self):
        return 'attributes__' + self.type_object.field_name

    def make_query(self):
        return models.Q(attributes__attribute=self)

    @property
    def control_object(self):
        '''
            Получение стратегии для работы с элементом для отображения свойства в фильтре

            .. versionadded:: 0.1
        '''
        if getattr(self, '_control_object', None) is None:
            self._control_object = AttributeManager.get_control(self.control)
        return self._control_object

    @property
    def type_object(self):
        '''
            Получение стратегии для работы с типом значений для свойства

            .. versionadded:: 0.1
        '''
        if getattr(self, '_type_object', None) is None:
            self._type_object = AttributeManager.get_type(self.type)
        return self._type_object

    def save(self, *args, **kwargs):
        '''
            При изменении типа надо поменять тип у всех существующих значений

            .. versionadded:: 0.1
        '''
        # Проверка на изменение типа
        is_changed = False
        if self.pk is not None:
            orig = Attribute.objects.get(pk=self.pk)
            is_changed = orig.type != self.type

        super(AttributeBase, self).save(*args, **kwargs)

        if is_changed:
            for product_attribute in ProductAttribute.objects.filter(attribute=self):
                product_attribute.save()

    def __unicode__(self):
        return self.title


# ------------------------------------------------------------------------------
class ProductAttributeBase(cache_machine.CachingMixin, models.Model):
    """Базовая модель для хранения значения свойства у продукта"""
    __metaclass__ = DeferredModelMetaclass.for_point(
        ProductAttribute,
        ImportProductAttributeValuesMetaclass,
        extend_meta(
            verbose_name=u'Значение свойства',
            verbose_name_plural=u'Значения свойства'
        )
    )

    class Meta:
        abstract = True

    product = DeferredForeignKey(Product, null=False, related_name='attributes')
    attribute = DeferredForeignKey(Attribute, null=False, related_name='values')

    # string_value = models.CharField(verbose_name=u"Значение", max_length=255)
    raw_value = models.CharField(verbose_name=u"Значение", max_length=255, blank=True, null=True)

    objects = CachingManager()

    @property
    def value(self):
        '''
        Получение типизированного значения свойства для продукта
        '''
        type_obj = self.attribute.type_object
        field_name = type_obj.field_name
        return getattr(self, field_name, type_obj.filter_value(self.raw_value))

    @value.setter
    def value(self, value):
        type_obj = self.attribute.type_object
        field_name = type_obj.field_name
        self.raw_value = unicode(value)
        setattr(self, field_name, type_obj.filter_value(value))

    def save(self, *args, **kwargs):
        for type_name, type_obj in AttributeManager.get_types():
            setattr(self, type_obj.field_name, None)

        # Точное обновление аргумента при сохранении
        type_obj = self.attribute.type_object
        setattr(self, type_obj.field_name, type_obj.filter_value(self.raw_value))

        super(ProductAttributeBase, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s: %s" % (self.attribute.title, unicode(self.value))


# ------------------------------------------------------------------------------
class SectionAttributeBase(cache_machine.CachingMixin, models.Model):
    """Базовая модель для настройки свойства в отдельном разделе"""
    __metaclass__ = DeferredModelMetaclass.for_point(
        SectionAttribute,
        extend_meta(
            verbose_name=u'Параметры для свойства в разделе',
            verbose_name_plural=u'Параметры для свойств в разделе',
            ordering=['order', 'attribute__main_title', 'id']
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
    """
        Базовая модель для псевдо раздела в каталоге

        .. note::
            Название url'а для обработки ``catalog:pseudo_section`` с параметрами
            ``slug`` (ЧПУ из раздела) и ``pseudo_slug`` (ЧПУ из псевдо-категории)

        .. versionadded:: 0.1
    """
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

    # Это новая цена
    price_from = models.DecimalField(verbose_name=u"Цена от", default=None, decimal_places=2, max_digits=10, null=True, blank=True)
    price_to = models.DecimalField(verbose_name=u"Цена до", default=None, decimal_places=2, max_digits=10, null=True, blank=True)

    def __unicode__(self):
        return ' '.join([self.section.title, ' > ', self.title])

    @models.permalink
    def get_absolute_url(self):
        '''
        Получение URL'а для просмотра экземпляра модели

        .. versionadded:: 0.2
        '''
        return ('catalog:pseudo_section', (), {'slug': self.section.slug, 'pseudo_slug': self.slug})


# ------------------------------------------------------------------------------
class PseudoSectionValueBase(models.Model):
    """
        Значение для фильтра псевдо-категории

        .. versionadded:: 0.1
    """
    __metaclass__ = DeferredModelMetaclass.for_point(
        PseudoSectionValue,
        ImportPseudoAttributeValuesMetaclass,
        extend_meta(
            verbose_name=u'Значение свойства в псевдо разделе',
            verbose_name_plural=u'Значения свойств в псевдо разделе'
        )
    )

    class Meta:
        abstract = True

    pseudo_section = DeferredForeignKey(PseudoSection, verbose_name=u'Псевдо раздел')
    attribute = DeferredForeignKey(Attribute, verbose_name=u'Свойство')

    raw_value = models.CharField(verbose_name=u"Значение", max_length=255, blank=True, null=True)
    raw_value_to = models.CharField(verbose_name=u"Значение (до)", max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        for type_name, type in AttributeManager.get_types():
            if not type.is_range:
                setattr(self, type.field_name, None)
            else:
                setattr(self, type.range_names[0], None)
                setattr(self, type.range_names[1], None)

        # Точное обновление аргумента при сохранении
        type = self.attribute.type_object
        if not type.is_range:
            setattr(self, type.field_name, type.filter_value(self.raw_value))
        else:
            setattr(self, type.range_names[0], type.filter_value(self.raw_value))
            setattr(self, type.range_names[1], type.filter_value(self.raw_value_to))

        super(PseudoSectionValueBase, self).save(*args, **kwargs)

    @property
    def value(self):
        '''
        Получение типизированного значения свойства для продукта

        .. versionadded:: 0.1
        '''
        type = self.attribute.type_object
        field_name = type.range_names[0] if type.is_range else type.field_name
        return getattr(self, field_name, type.filter_value(self.raw_value))

    @property
    def value_to(self):
        '''
        Получение типизированного значения свойства для продукта

        .. versionadded:: 0.1
        '''
        type = self.attribute.type_object
        field_name = type.range_names[1] if type.is_range else type.field_name
        return getattr(self, field_name, type.filter_value(self.raw_value_to))


# ------------------------------------------------------------------------------
class PseudoSectionBrandBase(models.Model):
    """
        Брэнды для фильтра псевдо-категории

        .. versionadded:: 0.1
    """
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
