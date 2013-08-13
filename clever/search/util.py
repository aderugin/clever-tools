# -*- coding: utf-8 -*-
from haystack.query import SearchQuerySet
from haystack.query import EmptySearchQuerySet
import re

quotes_re = re.compile(r'([\'"].*?[\'"])', re.S)


def filter_phrase(query, phrase):
    return query.filter_or(text__startswith=phrase) \
                .filter_or(text__contains="*" + phrase + "*") \
                .filter_or(text__exact="*" + phrase + "*") \
                .filter_or(text=phrase)


def make_queryset(
        query_string,
        queryset_class=SearchQuerySet,
        empty_queryset_class=EmptySearchQuerySet):
    query_string = query_string.strip()
    if query_string:
        # Разбиваем на группы для поиска
        query_parts = []
        query_quotes = quotes_re.split(query_string)
        query_quotes = filter(None, [qp.strip() for qp in query_quotes])
        for qp in query_quotes:
            if qp[0] == '"' or qp[0] == "\"":
                query_parts.append(qp[1:-1])
            else:
                query_spaces = filter(None, [
                    qp.strip() for qp in qp.split(' ')
                ])
                for qs in query_spaces:
                    query_parts.append(qs)

        # Включаем эти группы в поиск
        queryset = queryset_class()
        for qp in query_parts:
            queryset_part = filter_phrase(queryset_class(), qp)

            suggestion = SearchQuerySet().filter(text__startswith=qp) \
                                         .spelling_suggestion()
            if suggestion:
                queryset_part &= filter_phrase(queryset_part, suggestion)
            queryset &= queryset_part
        return queryset
    else:
        queryset = empty_queryset_class()
    return queryset
