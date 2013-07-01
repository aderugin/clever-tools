# -*- coding: utf-8 -*-
from haystack.query import SearchQuerySet, EmptySearchQuerySet
#from mistress_dream.apps.recipes.models import Recipe
from django.views.generic import ListView


##============================================================================##
class SearchView(ListView):
    def get_queryset(self):
        query = self.request.GET.get("q", '')
        if query:
            results = SearchQuerySet().auto_query(query)
        else:
            results = EmptySearchQuerySet()
        return results

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
