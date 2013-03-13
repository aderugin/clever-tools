# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from clever.catalog.metadata import CatalogMetadata
from clever.catalog.models import AttributeParams
import operator


class FilterForm(forms.Form):
    def get_product_model(self):
        if not getattr(self, 'product_model', None):
            raise RuntimeError("Для формы с фильтром продукции в разделе, не указана модель продукта в каталоге")
        return self.product_model


    def __init__(self, section, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

        self.section = section
        self.metadata = CatalogMetadata(self.get_product_model())

        # Получаем брэнды для фильтрации
        self.brands = self.get_brands()
        self.fields['brand'] = self.create_brand_field(self.brands)

        # Получаем аттрибуты для фильтрации
        self.attributes_params = self.get_attributes(section)
        for attr, values in self.attributes_params:
            # Создаем настоящий вид элемента
            attr_name = 'attribute-' + str(attr.id)
            control_object = attr.control_object

            self.fields[attr_name] = control_object.create_form_field(attr, values)


    def get_queryset(self):
        product_model = self.get_product_model()

        filter_args = ()
        filter_kwargs = {}
        if self.is_valid():
            # Фильтрация по брэндам
            brands = self.cleaned_data['brand']
            if brands:
                filter_kwargs['brand__in'] = brands

            # Фильтрация по значениям аттрибутов
            for attr, values in self.attributes_params:
                attr_name = 'attribute-' + str(attr.id)
                values = self.cleaned_data[attr_name]

                type_object = attr.type_object
                control_object = attr.control_object

                if values:
                    filter_args += (models.Q(attributes__attribute=attr) & control_object.create_query_part(attr, values), )

        return product_model.products.filter(section=self.section).filter(*filter_args, **filter_kwargs)


    def get_brands(self):
        return self.metadata.brand_model.objects.filter(products__section=self.section).distinct()


    def get_attributes(self, section):
        """Создание запроса для получение всех аттрибутов из данного раздела"""
        attribute_model = self.metadata.attribute_model
        section_attribute_model = self.metadata.section_attribute_model
        product_attribute_model = self.metadata.product_attribute_model

        # TODO: Refactoring!!! Здесь хуева туча по времени для запросов.

        # Поиск всех аттрибутов
        attributes = attribute_model.objects.filter(attributes__product__section=self.section).order_by('additional_title', 'main_title').distinct()
        attributes = list(attributes)

        # TODO: Поиск параметров аттрибутов для раздела

        # Поиск значений аттрибутов для раздела
        # values_list - не поддерживается :(
        attributes_values = product_attribute_model.objects.filter(attribute__in=attributes).distinct()
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


    def create_brand_field(self, brands):
        """Создание поля формы для брэнда"""
        return forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            label='Бренды',
            choices=[(unicode(str(brand.id)), brand.title) for brand in brands],
            required=False
        )
