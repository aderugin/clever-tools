# -*- coding: utf-8 -*-
from django.views.generic import ListView
from clever.search.util import make_queryset
from haystack.query import SearchQuerySet
from haystack.query import EmptySearchQuerySet



##============================================================================##
class SearchView(ListView):
    queryset_class = SearchQuerySet
    empty_queryset_class = EmptySearchQuerySet

    def get_queryset(self):
        query = self.request.GET.get("q", '')
        return make_queryset(query, queryset_class=self.queryset_class, empty_queryset_class=self.empty_queryset_class)

    def get_context_data(self, *args, **kwargs):
        context = super(SearchView, self).get_context_data(*args, **kwargs)
        query = self.request.REQUEST.get("q", '')
        result_objects = []
        for item in context['object_list']:
            result_objects.append(item.object)
        context.update({
            'query': query,
            'search_query': query,
            'result_objects': result_objects,
        })
        return context
