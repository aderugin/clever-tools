# -*- coding: utf-8 -*-
from clever.markup.extensions import PageExtension
from django.core.urlresolvers import reverse

class BreadcrumbsExtension(PageExtension):
    def process_page(self, page, request, context):
        # add breadcrumbs to request
        for page_id, page_title in page.breadcrumbs:
            page_url = reverse('markup:page', kwargs={'id': page_id})
            request.breadcrumbs(page_title, page_url)
