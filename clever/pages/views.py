# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from .models import Page
from django.http import Http404
from clever.core import views


class PageBreadcrumbsMixin(views.BreadcrumbsMixin):
    @property
    def page(self):
        raise NotImplementedError()

    def prepare_breadcrumbs(self, breadcrumbs, context):
        self.page
        for parent in self.page.get_ancestors(include_self=True):
            breadcrumbs(parent.title, parent.get_absolute_url())


class PageView(PageBreadcrumbsMixin, DetailView):
    model = Page
    context_object_name = 'page'
    template_name = None
    _page = None

    @property
    def page(self):
        if not self._page:
            self._page = get_object_or_404(Page, path=self.request.path, active=1)
        return self._page

    def get_object(self):
        return self.page

    def get_template_names(self):
        return [
            self.template_name,
            "pages/%s.jhtml" % self.page.slug,
            "pages/%s.html" % self.page.slug,
            "pages/%s_view.jhtml" % self.page.slug,
            "pages/%s_view.html" % self.page.slug,
            "layouts/%s.jhtml" % self.page.template,
            "layouts/%s.html" % self.page.template,
            "templates/%s.jhtml" % self.page.template,
            "templates/%s.html" % self.page.template,
            'page/default.jhtml',
            'page/default.html',
        ]


class PageMixin(object):
    _page = None
    page_slug = None

    @property
    def page(self):
        if not self._page:
            try:
                if not self.page_slug:
                    raise AttributeError("Page mixin detail view %s must be called with a page_slug." % self.__class__.__name__)

                page = Page.objects.get(slug=self.page_slug)
                if not page.active:
                    raise Http404()
                self._page = page
            except Page.DoesNotExist:
                self._page = None
        return self._page

    def get_context_data(self, **kwargs):
        context = super(PageMixin, self).get_context_data(**kwargs)
        context.update({
            'page': self.page
        })
        if not isinstance(self, DetailView):
            context.update({
                'object': self.page
            })
        return context
