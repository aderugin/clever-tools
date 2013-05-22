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
from django.core.paginator import Paginator
from django.core.paginator import InvalidPage
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.translation import ugettext as _
from clever.catalog import models
from clever.catalog.models import Product


# ------------------------------------------------------------------------------
class IndexView(ListView):
    """Главная страница каталога"""
    def get_queryset(self):
        return self.model.sections.get_query_set()


# ------------------------------------------------------------------------------
class BrandIndexView(ListView):
    """Главная страница каталога"""
    def get_queryset(self):
        return self.model.brands.get_query_set()


# ------------------------------------------------------------------------------
class BrandView(DetailView):
    """Страница для просмотра отдельного бренда"""

    def get_queryset(self):
        return self.model.brands.get_query_set()

    def get_sections_queryset(self, brand):
        return brand.descendant_sections

    def get_context_data(self, **kwargs):
        context = super(BrandView, self).get_context_data(**kwargs)
        context['section_list'] = self.get_sections_queryset(self.get_object())
        return context


# ------------------------------------------------------------------------------
class SectionView(DetailView):
    """Страница для просмотра отдельного раздела"""
    pseudo_section = None
    allow_empty = True
    paginate_by = None
    paginator_class = Paginator
    page_kwarg = 'page'
    count_kwarg = 'count'
    order_by = {
        # TODO: Добавить сортировку по идентификатору
    }
    default_order = None

    def get_queryset(self):
        return self.model.sections.get_query_set()

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset, if needed.
        """
        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_("Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
                'page_number': page_number,
                'message': str(e)
            })

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        count_kwarg = self.count_kwarg
        paginate_by = None
        if self.paginate_by:
            paginate_by = self.kwargs.get(count_kwarg) or self.request.GET.get(count_kwarg) or self.paginate_by
            try:
                paginate_by = int(paginate_by)
            except ValueError:
                pass

        # Если количество указано all - отключить paginator
        if paginate_by == 'all':
            return None
        return paginate_by

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        """
        Return an instance of the paginator for this view.
        """
        return self.paginator_class(queryset, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)

    def get_allow_empty(self):
        """
        Returns ``True`` if the view should display empty lists, and ``False``
        if a 404 should be raised instead.
        """
        return self.allow_empty

    def get_filter_form(self, *args, **kwargs):
        """Получение формы для фильтра"""
        filter_form = getattr(self, 'filter_form', None)
        if filter_form and not getattr(self, '_filter_form', None):
            # Подготовка фильтра для псевдо раздела
            data = kwargs.get('data', self.request.GET).copy()
            pseudo_section = self.get_pseudo_section()
            if pseudo_section:
                data = self.prepare_pseudo_section(self.pseudo_section, data)
                kwargs = kwargs.copy()
            kwargs['data'] = data

            # Создание фильтра
            self._filter_form = filter_form(self.get_object(), *args, **kwargs)

        return getattr(self, '_filter_form', None)

    def get_pseudo_section_queryset(self):
        """Создание запроса для получения активной псевдо категорий из раздела"""
        return models.PseudoSection.pseudo_sections.active()

    def get_pseudo_section(self):
        """Получение активной псевдо категорий из раздела"""
        pseudo_slug = self.kwargs.get('pseudo_slug', None)
        if pseudo_slug and not self.pseudo_section:
            queryset = self.get_pseudo_section_queryset()
            self.pseudo_section = get_object_or_404(klass=queryset, section=self.get_object(), slug=pseudo_slug)
        return self.pseudo_section

    def get_pseudo_sections_queryset(self):
        """Создание запроса для получения все активных псевдо категорий из раздела"""
        queryset = models.PseudoSection.pseudo_sections.filter(section=self.get_object())
        return queryset

    def get_products_queryset(self):
        """Создание запроса для получения продуктов из раздела"""
        return Product.products.filter(section=self.get_object())

    def get_filter_queryset(self, queryset):
        filter_form = self.get_filter_form()
        if filter_form:
            queryset = filter_form.get_queryset(queryset)
        return queryset

    def get_order_by(self, queryset):
        order = self.request.GET.get('order_by', self.default_order)
        sort_by = self.request.GET.get('sort_by', 'asc')
        if not order in self.order_by:
            order = self.default_order
        if order in self.order_by and order is not None:
            order_by = self.order_by[order]
            result_order = order_by['fields']
            for field in range(len(result_order)):      # TODO
                if sort_by == 'desc':
                    if result_order[field][0] != '-':
                        result_order[field] = '-' + result_order[field]
                if sort_by == 'asc' and result_order[field][0] == '-':
                    result_order[field] = result_order[field][1:]
            queryset = queryset.order_by(*result_order)

        return order, sort_by, queryset

    def get_sections_queryset(self):
        return self.get_object().children.all()

    def prepare_pseudo_section(self, pseudo_category, filter_data):
        ''' Подготовка данных для формы фильтра '''
        # Фильтр по брэндам
        brands = models.Brand.brands.filter(pseudo_section_brands__pseudo_section=pseudo_category).values_list('id')
        for brand in brands:  # Хак, для flatten list of list
            filter_data.appendlist('brand', int(brand[0]))
        return filter_data

    def get_context_data(self, **kwargs):
        context = super(SectionView, self).get_context_data(**kwargs)

        # Получаем форму с фильтром и псевдо разделы для текущего раздела каталога
        context.update({
            'section_list': self.get_sections_queryset(),
            'filter_form': self.get_filter_form(),
            'pseudo_sections': self.get_pseudo_sections_queryset(),
            'active_pseudo_section': self.get_pseudo_section(),
        })

        # Получаем продукты для текущего раздела каталога
        products_queryset = self.get_products_queryset()
        products_queryset = self.get_filter_queryset(products_queryset)

        # сортируем queryset перед выдачей
        order_by, sort_by, products_queryset = self.get_order_by(products_queryset)
        page_size = self.get_paginate_by(products_queryset)
        if page_size:
            paginator, page, products_queryset, is_paginated = self.paginate_queryset(products_queryset, page_size)
            context.update({
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'products': products_queryset
            })
        else:
            context.update({
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'products': products_queryset
            })

        # Получем информацию для сортировки
        sort_list = []
        for key, params in self.order_by.items():
            sort_name = params['title']
            sort = 'asc'
            if order_by == key:
                sort = 'asc' if sort_by == 'desc' else 'desc'
            sort_list.append([sort_name, key, sort])

        context.update({
            'order_by': order_by,
            'sort_by': sort_by,
            'sort_list': sort_list,
        })

        # Получем метаинформацию: заголовок и текст страницы раздела
        if context['active_pseudo_section']:
            meta_object = context['active_pseudo_section']
        else:
            meta_object = self.get_object()
        context.update({
            'section_title': meta_object.title,
            'section_text': meta_object.text,
            'section_url': meta_object.get_absolute_url(),
        })

        # Возвращаем все
        return context


# ------------------------------------------------------------------------------
class ProductView(DetailView):
    """Страница для просмотра отдельного продукта"""

    def get_queryset(self):
        return self.model.products.get_query_set()

    def get_attributes(self):
        return models.ProductAttribute.objects.filter(product=self.get_object())

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)

        context['attributes'] = self.get_attributes()

        # Возвращаем все
        return context
