# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.core.exceptions import FieldError
from django.http import Http404
from django.views.generic import View
from importlib import import_module


shared_views = {}


class SharedView(View):
    regex = None

    @property
    def views(self):
        if self.regex and self.regex in shared_views:
            return shared_views[self.regex]
        else:
            return []

    def dispatch(self, request, *args, **kwargs):
        for v in self.views:
            view = v()
            if hasattr(view, 'get_shared_queryset'):
                shared_queryset = view.get_shared_queryset()
            else:
                shared_queryset = view.get_queryset()

            try:
                if shared_queryset.filter(**kwargs).count() > 0:
                    menu_path = getattr(v, 'menu_path', None)
                    if menu_path:
                        request.menu_path = menu_path
                    return v.as_view()(request, *args, **kwargs)
            except FieldError:
                # поиск производится по разным типам моделей и их поля отличаются
                pass
        raise Http404()


def shared_urlpatterns(regex, *rules):
    """
    Группа урлов с одним паттерном. (Добавлять в самый конец корневого urlpatterns)

    Аргументы:
        regex - паттерн для урлов в группе
        *rules - кортежи урлов (view_class, name[, namespace])

    'если namespace не указан, то используется имя приложения
    """
    patterns_list = []

    for rule in rules:
        if len(rule) > 2:
            namespace = rule[2]
        else:
            namespace = None
        #     namespace = rule[0].__module__.split('.')[-2]
        url_item = url(regex, SharedView.as_view(regex=regex), name=rule[1])
        urls_mod = import_module(settings.ROOT_URLCONF)
        urlpatterns = getattr(urls_mod, 'urlpatterns')

        for resolver in urlpatterns:
            if namespace == getattr(resolver, 'namespace', None):
                resolver.url_patterns.append(url_item)
                continue

        patterns_list.append(
            url('', include((
                patterns('', url_item),
                None,
                namespace
            )))
        )

    shared_views[regex] = [r[0] for r in rules]
    return patterns('', *patterns_list)

