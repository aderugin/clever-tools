# -*- coding: utf-8 -*-
"""
:mod:`clever.catalog.view` -- Виды для базового каталога
========================================================

В данном модуле хранится базовый набор видов для работы с каталогом.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
"""

from __future__ import absolute_import
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from clever.catalog.metadata import CatalogMetadata


class IndexView(ListView):
    """Главная страница каталога"""
    def get_queryset(self):
        return self.model.sections.get_query_set()


class BrandIndexView(ListView):
    """Главная страница каталога"""
    def get_queryset(self):
        return self.model.brands.get_query_set()


class BrandView(DetailView):
    """Страница для просмотра отдельного бренда"""
    def get_queryset(self):
        return self.model.brands.get_query_set()

    def get_sections_queryset(self, brand):
        if not getattr(self, 'section_model', None):
            raise RuntimeError("Для страницы детальной информации о бренде, не указана модель раздела в каталоге")
        section_model = self.section_model
        return section_model.sections.filter(products__brand=brand).distinct()

    def get_context_data(self, **kwargs):
        context = super(BrandView, self).get_context_data(**kwargs)
        context['section_list'] = self.get_sections_queryset(self.get_object())
        return context


class SectionView(DetailView):
    """Страница для просмотра отдельного раздела"""
    pseudo_section = None

    def get_queryset(self):
        return self.model.sections.get_query_set()

    def get_filter_form(self, *args, **kwargs):
        """Получение формы для фильтра"""
        filter_form = getattr(self, 'filter_form', None)
        if filter_form and not getattr(self, '_filter_form', None):
            self._filter_form = filter_form(self.get_object(), *args, **kwargs)
        return getattr(self, '_filter_form', None)

    def get_pseudo_section(self):
        """Создание запроса для получения активной псевдо категорий из раздела"""
        pseudo_slug = self.kwargs.get('pseudo_slug', None)
        if pseudo_slug and not self.pseudo_section:
            if not getattr(self, 'pseudo_section_model', None):
                raise RuntimeError("Для страницы детальной информации о разделе, не указана форма фильтра или модель продукта в каталоге")
            pseudo_section_model = self.pseudo_section_model
            self.pseudo_section = get_object_or_404(klass=pseudo_section_model.pseudo_sections, section=self.get_object(), slug=pseudo_slug)
        return self.pseudo_section

    def get_pseudo_queryset(self):
        """Создание запроса для получения все активных псевдо категорий из раздела"""
        if not getattr(self, 'pseudo_section_model', None):
            raise RuntimeError("Для страницы детальной информации о разделе, не указана форма фильтра или модель продукта в каталоге")
        pseudo_section_model = self.pseudo_section_model
        queryset = pseudo_section_model.pseudo_sections.filter(section=self.get_object())
        return queryset

    def get_products_queryset(self):
        """Создание запроса для получения продуктов из раздела"""
        filter_form = self.get_filter_form()
        if filter_form:
            queryset = filter_form.get_queryset()
        else:
            if not getattr(self, 'product_model', None):
                raise RuntimeError("Для страницы детальной информации о разделе, не указана форма фильтра или модель продукта в каталоге")
            product_model = self.product_model
            queryset = product_model.products.filter(section=self.get_object())
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SectionView, self).get_context_data(**kwargs)

        # Получаем форму с фильтром
        context['filter_form'] = self.get_filter_form()

        # Получаем псевдо разделы для текущего раздела каталога
        context['pseudo_sections'] = self.get_pseudo_queryset()
        context['active_pseudo_section'] = self.get_pseudo_section()

        # Получаем продукты для текущего раздела каталога
        context['products'] = self.get_products_queryset()

        # Возвращаем все
        return context

    def post(self, request, *args, **kwargs):
        """Обрабатываем запрос к базе данный"""
        self.get_filter_form(request.POST, request.FILES)
        return self.get(self, request, *args, **kwargs)


class ProductView(DetailView):
    """Страница для просмотра отдельного продукта"""

    def __init__(self, *args, **kwargs):
        super(ProductView, self).__init__(*args, **kwargs)
        self.metadata = CatalogMetadata(self.model)

    def get_queryset(self):
        return self.model.products.get_query_set()

    def get_main_attributes(self):
        return []

    def get_nonmain_attributes(self):
        return self.metadata.product_attribute_model.objects.filter(product=self.get_object())

    def get_attributes(self):
        return self.get_nonmain_attributes(), self.get_main_attributes()

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)

        context['attributes'], context['main_attributes'] = self.get_attributes()

        # Возвращаем все
        return context
