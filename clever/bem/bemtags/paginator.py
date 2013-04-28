# -*- coding: utf-8 -*-
from clever.bem.base import BemTag


# ------------------------------------------------------------------------------
class PaginatorTag(BemTag):
    ''' Подготовка данных для paginator '''

    def get_bemjson_context(self, request, context):
        paginator = context['paginator']
        page = context['page_obj'];

        if not paginator:
            return None

        return {
            'block': 'b-pagination',
            'content': 'Test paginator',

            'query': '',
            'current': page.number,
            'first': 1,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'last': paginator.num_pages,
            'pages': paginator.page_range
        }
