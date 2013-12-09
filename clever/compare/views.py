# -*- coding: utf-8 -*-

from django.views import generic
from clever.core.views import AjaxMixin
from . import models
from clever.catalog.models import Product
from django.core import urlresolvers
from django import http


class NextView(generic.RedirectView):
    permanent = False
    status = False

    def proccess(self, request, comparer):
        raise NotImplementedError()

    def get(self, request, *args, **kwargs):
        comparer = models.Comparer.load(request)
        self.status = self.proccess(request, comparer)
        comparer.save(request)

        return super(NextView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        next = self.request.GET.get('next', '/')
        return next


class AddView(AjaxMixin, NextView):
    def proccess(self, request, comparer):
        product_id = self.kwargs.get('id', None)
        self.product = Product.objects.get(id=product_id)
        if self.product:
            comparer.add(self.product.id)
            return True

    def get_ajax_data(self, **kwargs):
        if self.product:
            return {
                'status': self.status,
                'group': {
                    'id': self.product.section.id,
                    'title': self.product.section.title,
                    'url': self.product.section.get_absolute_url(),
                    'compare_url': urlresolvers.reverse('compare:index') + '?section=' + str(self.product.section.id),
                },
                'product': {
                    'id': self.product.id,
                    'title': self.product.title,
                    'url': self.product.get_absolute_url(),
                }
            }
        return {'status': False}


class RemoveView(AjaxMixin, NextView):
    def proccess(self, request, comparer):
        product_id = self.kwargs.get('id', None)
        self.product = Product.objects.get(id=product_id)
        if self.product:
            comparer.remove(self.product.id)
            return True

    def get_ajax_data(self, **kwargs):
        if self.product:
            return {
                'status': self.status,
                'product_id': self.product.id
            }
        return {'status': False}


class ClearView(AjaxMixin, NextView):
    def proccess(self, request, comparer):
        group_id = self.kwargs.get('id', None)
        print group_id
        if group_id:
            comparer.clear_group(group_id)
        else:
            comparer.clear()
        return True

    def get_ajax_data(self, **kwargs):
        return {'status': True}


class StatusView(AjaxMixin, generic.TemplateView):
    template_name = 'base.html'

    def get_ajax_data(self, **kwargs):
        comparer = models.Comparer.load(self.request)
        context = []
        for group in comparer:
            items = []
            for product in group.items:
                items.append({
                    'id': product.id,
                    'title': product.title,
                    'url': product.get_absolute_url(),
                })
            context.append({
                'id': group.section.id,
                'title': group.section.title,
                'items': items,
                'url': group.section.get_absolute_url(),
                'compare_url': urlresolvers.reverse('compare:index') + '?section=' + str(group.section.id),
            })
        return context


class CompareView(generic.TemplateView):
    template_name = 'compare/compare_view.html'
    comparer = None

    strategies = {
        'all': models.AllStrategy(),
        'diff': models.DifferentStrategy(),
    }

    def get_strategies(self):
        return self.strategies

    def get_comparer(self):
        if not self.comparer:
            self.comparer = models.Comparer.load(self.request)
        return self.comparer

    def get_groups(self):
        ''' Получение списка групп для сравнения и текущей группы '''
        comparer = self.get_comparer()
        groups = comparer.get_groups()

        # Не отображать пустое сравнение
        if len(groups) == 0:
            raise http.Http404(u'Нет нечего для сравнения')

        # Ищем раздел для сравнения
        section_id = self.request.GET.get('section', None)
        if section_id is None:
            section_id = groups[0].id
        else:
            section_id = int(section_id)

        # Активный раздел
        active = None
        for group in groups:
            if group.id == section_id:
                active = group
                break
        if not active:
            raise http.Http404(u'Нет нечего для сравнения')
        return active, groups

    def prepare_strategy(self):
        # Получаем стратегию сравнения
        strategy_name = self.request.GET.get('strategy', 'all')
        strategies = self.get_strategies()
        if strategy_name not in strategies:
            strategy_name = 'all'
        strategy = strategies[strategy_name]
        return strategy_name, strategy

    def mark_strategy(self, attributes):
        strategies = self.get_strategies()
        for temp_name, strategy in strategies.items():
            print temp_name
            for attribute in attributes:
                is_compare =strategy.compare(attribute, attribute.compared_values)
                compare_name = 'is_compare_' + temp_name
                setattr(attribute, compare_name, is_compare)

    def prepare_attributes(self, attributes):
        return attributes

    def get_context_data(self, **kwargs):
        context = super(CompareView, self).get_context_data(**kwargs)
        active, groups = self.get_groups()
        strategy_name, strategy = self.prepare_strategy()

        # Аттрибуты
        attributes = active.compare_attributes(strategy)
        attributes = self.prepare_attributes(attributes)

        # Если смотрем все свойства отмечаем остальные
        if strategy_name == 'all':
            self.mark_strategy(attributes)

        context.update({
            'active': active,
            'groups': groups,
            'strategy': strategy_name,

            'products': active.items,
            'attributes': attributes,
        })
        return context
