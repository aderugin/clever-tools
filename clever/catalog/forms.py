# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from clever.catalog.models import AttributeManager
from clever.catalog.models import Attribute
from clever.catalog.models import SectionAttribute
from clever.catalog.models import SectionBrand
from clever.catalog.models import Product
from clever.catalog.models import ProductAttribute
import operator


class FilterForm(forms.Form):
    ''' Базовая форма для фильтра '''
    def __init__(self, section, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

        self.section = section

        # Получаем аттрибуты для фильтрации
        self.attributes_params = self.get_pseudo_attributes(section) + self.get_attributes(section)
        for attr, values in self.attributes_params:
            # Создаем настоящий вид элемента
            control_object = attr.control_object

            self.fields[attr.uid] = control_object.create_form_field(attr, values)

    def get_queryset(self):
        filter_args = ()

        if self.is_valid():
            # Фильтрация по значениям аттрибутов
            for attr, values in self.attributes_params:
                values = self.cleaned_data[attr.uid]

                # type_object = attr.type_object
                control_object = attr.control_object
                if values:
                    # Получение параметров для query
                    attr_query = attr.make_query()
                    values_query = control_object.create_query_part(attr, values)
                    if attr_query:
                        attr_query &= values_query
                    else:
                        attr_query = values_query
                    filter_args += (values_query,)
        else:
            for name, message in self.errors.items():
                print name, message

        products_queryset = Product.products.filter(section=self.section)
        if len(filter_args):
            products_queryset = products_queryset.filter(models.Q(reduce(operator.and_, filter_args)))
        return products_queryset

    def get_pseudo_attributes(self, section):
        """Получение всех псевдо аттрибутов из данного раздела"""
        # Подготовка значений к выводу
        final_result = []

        # Поиск значений для псевдо свойств
        for attrib in AttributeManager.get_attributes():
            values = attrib.get_values(section)
            final_result.append((attrib, values,))
        return final_result

    def get_attributes(self, section):
        """Создание запроса для получение всех аттрибутов из данного раздела"""

        # TODO: Refactoring!!! Здесь хуева туча по времени для запросов.

        # Поиск всех аттрибутов
        attributes = Attribute.objects.filter(values__product__section=self.section).order_by('additional_title', 'main_title').distinct()
        attributes = list(attributes)

        # TODO: Поиск параметров аттрибутов для раздела

        # Поиск значений аттрибутов для раздела
        # values_list - не поддерживается :(
        attributes_values = ProductAttribute.objects.filter(attribute__in=attributes).distinct()
        attributes_values = list(attributes_values)

        # Подготовка значений к выводу
        final_result = []
        for attrib in attributes:
            values = []
            for product_attrib in attributes_values:
                if attrib.id == product_attrib.attribute_id:
                    value = product_attrib.value
                    values.append((value, value))
            final_result.append((attrib, values,))
        return final_result
