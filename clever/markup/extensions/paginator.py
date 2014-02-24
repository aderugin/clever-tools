# -*- coding: utf-8 -*-
from clever.markup.extensions import PageExtension
from django.core.paginator import Paginator


class PaginatorExtension(PageExtension):
    def process_page(self, page, request, context):
        # if paginator add to context
        if page.is_paginator:
            paginator = Paginator([x for x in xrange(0, 1000)], request.GET.get('count', 20))
            page_obj = paginator.page(request.GET.get('page', 1))
            is_paginated = page_obj.has_other_pages()

            context.update({
                'paginator': paginator,
                'page_obj': page_obj,
                'is_paginated': is_paginated,
            })
