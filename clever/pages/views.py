# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from .models import Page
from django.http import Http404


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
            "pages/%s.jhtml" % self.page.slug,
            "pages/%s.html" % self.page.slug,
            "pages/%s_view.jhtml" % self.page.slug,
            "pages/%s_view.html" % self.page.slug,
            "layouts/%s.jhtml" % self.page.template,
            "layouts/%s.html" % self.page.template,
            "templates/%s.jhtml" % self.page.template,
            "templates/%s.html" % self.page.template,
        ]


class PageMixin(object):
    page = None
    page_slug = None

    def get_page(self):
        if not self.page:
            try:
                if not self.page_slug:
                    raise AttributeError("Page mixin detail view %s must be called with a page_slug." % self.__class__.__name__)

                self.page = Page.objects.get(slug=self.page_slug)
                if not self.page.active:
                    raise Http404()
            except Page.DoesNotExist:
               self.page = None
        return self.page

    def get_context_data(self, **kwargs):
        context = super(PageMixin, self).get_context_data(**kwargs)
        context.update({
            'page': self.get_page()
        })
        if not isinstance(self, DetailView):
            context.update({
                'object': self.get_page()
            });
        return context
