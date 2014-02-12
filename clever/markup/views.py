from django.views import generic
from clever.markup import pages
from django.http import HttpResponse


class IndexView(generic.View):
    def get(self, *args, **kwargs):
        manager = pages.Manager()
        return HttpResponse(manager.render_index())


class PageView(generic.View):
    def get(self, *args, **kwargs):
        id = kwargs.get('id')
        manager = pages.Manager()
        page = manager.pages[id]
        return HttpResponse(manager.render_page(page))
