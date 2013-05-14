# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from .models import Page


class PageView(DetailView):

    model = Page
    context_object_name = 'page'
    template_name = 'page/default.html'

    def get_object(self):

        page = get_object_or_404(Page, path=self.request.path, active=1)
        self.page = page
        return page

    def get_template_names(self):
        return [
            "pages/%s.html" % self.page.slug,
            "pages/%s_view.html" % self.page.slug,
            "layouts/%s.html" % self.page.template,
            "templates/%s.html" % self.page.template,
        ]
