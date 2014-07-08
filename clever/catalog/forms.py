# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from cache_tagging.django_cache_tagging import get_cache
from clever.catalog.models import AttributeManager, AttributeGroup
from clever.catalog.models import Attribute
from clever.catalog.models import SectionAttribute
from clever.catalog.models import Product
from clever.catalog.models import ProductAttribute
from clever.catalog.settings import CLEVER_FILTER_TIMEOUT
from functools import wraps
import hashlib
import logging
import operator
import sys
import pickle


def md5(object):
    string = pickle.dumps(object)
    m = hashlib.md5()
    m.update(string)
    return m.hexdigest()

def filter_section_cached(func=None, prefix=None):
    def wrapper(func):
        # cache = get_cache('catalog')
        cache = get_cache('catalog')
        log = logging.getLogger('clever.catalog')

        @wraps(func)
        def with_cache(self, section):
            cache_id = 'filter.section.%s.%d.%s' % (func.__name__, section.id, prefix)
            cache_tag = 'section.%d' % section.id
            cached_result = cache.get(cache_id)
            if not cached_result:
                log.info('Cache miss for filter: %s', cache_id)
                result = func(self, section)
                cached_result = pickle.dumps(result)
                cache.set(cache_id, cached_result, timeout=CLEVER_FILTER_TIMEOUT, tags=[cache_tag])
            else:
                log.info('Cache found for filter: %s', cache_id)
                result = pickle.loads(cached_result)
            return result
        return with_cache

    if callable(func):
        return wrapper(func)
    return wrapper


def filter_queryset_cached(func):
    # cache = get_cache('catalog')
    cache = get_cache('catalog')
    log = logging.getLogger('clever.catalog')

    @wraps(func)
    def with_cache(self, section, queryset):
        cache_id = 'filter.section.%s.%d' % (func.__name__, section.id)
        cache_tag = 'section.%d' % section.id
        if self.is_valid():
            cache_id = cache_id + '-' + md5(self.cleaned_data)
            log.info('Filter is valid: %s', cache_id)
            cached_result = cache.get(cache_id)
            if not cached_result:
                log.info('Cache miss for filter: %s', cache_id)
                product_indexes = func(self, section, queryset)
                cached_result = pickle.dumps(product_indexes)
                cache.set(cache_id, cached_result, timeout=CLEVER_FILTER_TIMEOUT, tags=[cache_tag])
            else:
                log.info('Cache found for filter: %s', cache_id)
                product_indexes = pickle.loads(cached_result)

            if product_indexes is not None:
                log.info('Products filtered by indexes')
                if len(product_indexes) > 0:
                    return queryset.filter(id__in=[v[0] for v in product_indexes])
                else:
                    return queryset.none()
        else:
            log.info('Filter is not valid: %s', cache_id)
        log.info('Products is not filtered')
        return queryset
    return with_cache


class FilterForm(forms.Form):
    ''' Базовая форма для фильтра '''
    def __init__(self, instance=None, sections=None, *args, **kwargs):

        super(FilterForm, self).__init__(*args, **kwargs)

        self.attributes = {}
        self.section = instance
        self.sections = sections if not sections is None else [self.section]

        # Получаем аттрибуты для фильтрации
        self.attributes_params = self.get_pseudo_attributes(instance) + self.get_attributes(instance)
        self.attributes_params = self.sort_attributes_params(self.attributes_params)

        # Формируем поля для фильтра
        for filter_attribute in self.attributes_params:
            self.fields[filter_attribute.uid] = filter_attribute.field
            self.attributes[filter_attribute.uid] = filter_attribute

    def sort_attributes_params(self, attributes_params):
        return sorted(attributes_params, key=lambda x: x.params.order if x.params is not None else sys.maxint)

    def get_queryset(self, products_queryset):
        return self.get_product_indexes(self.section, products_queryset)

    @filter_queryset_cached
    def get_product_indexes(self, section, queryset):
        filter_args = ()

        if self.is_valid():
            # Фильтрация по значениям аттрибутов
            for filter_attribute in self.attributes_params:
                attr = filter_attribute.attribute
                values = self.cleaned_data[attr.uid]

                # type_object = attr.type_object
                control_object = attr.control_object
                if values:
                    # Получение параметров для query
                    attr_query = attr.make_query()
                    values_query = control_object.create_query_part(attr, values)
                    if values_query:
                        if attr_query:
                            attr_query &= values_query
                        else:
                            attr_query = values_query
                        filter_args += (attr_query,)
        else:
            for name, message in self.errors.items():
                print name, message

        product_indexes = None
        for filter_arg in filter_args:
            current_indexes = set(Product.objects.filter(filter_arg, section__in=self.sections).values_list('id'))
            if product_indexes is not None:
                product_indexes &= current_indexes
            else:
                product_indexes = current_indexes
        return product_indexes

        if product_indexes is not None:
            if len(product_indexes) > 0:
                return products_queryset.filter(id__in=[v[0] for v in product_indexes])
            else:
                return products_queryset.none()
        else:
            return products_queryset

    @filter_section_cached
    def get_pseudo_attributes(self, section):
        """Получение всех псевдо аттрибутов из данного раздела"""
        # Подготовка значений к выводу
        final_result = []

        # Поиск значений для псевдо свойств
        for attrib in AttributeManager.get_attributes():
            values = attrib.get_values(self.sections)
            if len(values):
                final_result.append(FilterAttribute(section, attrib, values,))
        return final_result

    @filter_section_cached
    def get_attributes(self, section):
        """Создание запроса для получение всех аттрибутов из данного раздела"""
        # TODO: Refactoring!!! Здесь хуева туча по времени для запросов.
        # Поиск всех аттрибутов
        attributes = Attribute.objects.filter(is_filtered=True).order_by('additional_title', 'main_title').distinct()
        if len(self.sections):
            attributes = attributes.filter(values__product__section__in=self.sections)
        attributes = list(attributes)
        
        # Поиск значений аттрибутов для раздела
        attributes_values = ProductAttribute.objects.filter(attribute__in=attributes).values_list('attribute__id', 'raw_value').distinct()
        #attributes_values = ProductAttribute.objects.filter(attribute__in=attributes).select_related('attribute').distinct()
        if len(self.sections):
            attributes_values = attributes_values.filter(product__section__in=self.sections)
        attributes_values = list(attributes_values)
        
        # Поиск параметров аттрибутов для раздела
        attributes_params = SectionAttribute.objects.filter(attribute__in=attributes).select_related('attribute').distinct()
        if section:
            attributes_params = attributes_params.filter(section=self.section)
        attributes_params = list(attributes_params)

        # Подготовка значений к выводу
        final_result = []
        for attrib in attributes:
            values = []
            values_set = set()
            params = None

            # Поиск значений для свойства
            for product_attrib in attributes_values:

                #if attrib.id == product_attrib.attribute_id:
                #    value = product_attrib.value
                if attrib.id == product_attrib[0]:
                    value = product_attrib[1]
                    if not value in values_set:
                        values_set.add(value)
                        values.append((value, value))

            # Поиск параметра для свойства
            for section_attrib in attributes_params:
                if attrib.id == section_attrib.attribute_id:
                    params = section_attrib

            # Добавляем поле в финальный результат
            if len(values):
                type_object = attrib.type_object
                values = [(type_object.filter_value(v), t) for v, t in values]
                values = sorted(values)
                final_result.append(FilterAttribute(section, attrib, values, params))
        return final_result

    @property
    def attributes_list(self):
        return ((filter_attribute, self[filter_attribute.uid]) for filter_attribute in self.attributes_params)

    def compare_groups(self, group1, group2):
        return group1.title < group2.title

    @property
    def groups(self):
        # Merge attributes in groups
        group_dict = {}
        group_list = []

        for filter_attr, field in self.attributes_list:
            group_id = getattr(filter_attr.attribute, 'group_id', None)
            group = group_dict.get(group_id, None)
            if not group:
                group = FilterGroup()
                if group_id:
                    group_dict[group_id] = group
                    group.is_collapsable = True
                    group.collapse = True
                else:
                    group_list.append(group)
            group.fields.append((filter_attr, field, ))

        # Collect groups information
        indexes = [x for x in group_dict.keys() if x is not None]
        groups = AttributeGroup.objects.filter(id__in=indexes)
        for group in groups:
            group_dict[group.id].group = group

        # Sort groups
        groups = [x for x in sorted(group_dict.values(), self.compare_groups)] + group_list
        for group in groups:
            self.prepare_group(group)
        return groups

    def prepare_group(self, group):
        pass


class FilterAttribute(object):
    def __init__(self, section, attrib, values, params=None):
        self.section = section
        self.attribute = attrib
        self.attributes_values = values
        self.params = params

        control_object = self.attribute.control_object
        self.field = control_object.create_form_field(self.attribute, self.attributes_values)

    @property
    def uid(self):
        return self.attribute.uid

    def __unicode__(self):
        return unicode(self.attribute)

    def __repl__(self):
        return unicode(self.attribute).encode('utf-8')


class FilterGroup:
    is_collapsable = None
    collapse = None
    fields = None
    group = None

    def __init__(self):
        self.fields = []

    @property
    def is_single(self):
        return len(self.fields) == 1

    @property
    def first_attribute(self):
        return self.fields[0][0].attribute

    @property
    def title(self):
        if self.group:
            return self.group.title
        elif self.is_single:
            return self.first_attribute.title
        return ''

    @property
    def unit(self):
        if not self.group and self.is_single:
            return self.first_attribute.unit
        return ''