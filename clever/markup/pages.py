# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import loader
from django.template import Context
from django.template import RequestContext
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from clever.markup.metadata import fixture_factory
from clever.markup.metadata import MetadataError
from clever.fixture import load_fixture
from clever.fixture import FixtureNotFound
from clever.magic import load_class
from django.core.urlresolvers import reverse
import yaml
import os
import codecs
import logging


class Page:
    id = None
    title = None
    params = None

    is_paginator = False
    breadcrumbs = ()

    def __init__(self, id, title, params):
        self.id = id
        self.title = title
        self.params = params
        self.is_paginator = params.get('is_paginator', False)
        self.breadcrumbs = params.get('breadcrumbs', ())

    @property
    def template_name(self):
        ''' Получение пути к файлу шаблона для страницы '''
        return self.params.get('template', self.id + '.jhtml')

    @property
    def fixture_name(self):
        ''' Получение пути до файла с данными для страницы '''
        (template_root, template_ext) = os.path.splitext(self.template_name)
        return self.params.get('fixture', template_root + '.yaml')

    @property
    def output_name(self):
        return self.params.get('output', self.id + '.html')

    @property
    def url(self):
        ''' Получение URL для страницы '''
        return self.params.get('url', reverse('markup:page', kwargs={'id': self.id}))

    def load_template(self):
        ''' Load template '''
        return loader.get_template(self.template_name)

    def load_fixture(self):
        ''' Load fixture '''
        try:
            return load_fixture(self.fixture_name)
        except FixtureNotFound:
           return None


class Manager():
    fixture_factory = None
    request_factory = None
    pages = None

    def __init__(self, fixture_name='markup.yaml'):
        self.request_factory = RequestFactory()
        self.fixture_factory = fixture_factory
        self.pages = {}

        # Load fixture from file
        data = load_fixture(fixture_name)

        # Populate pages
        for id, params in data.items():
            id = str(id)
            title = params.get('title', '').strip()
            if not title:
                raise RuntimeError("Title for page %s is not found in file '%s'" % (id, fixture_name))
            page = Page(id, title, params)
            self.pages[id] = page

    def prepare_page(self, page, request, context):
        # prepare middlewares
        middlewares = settings.MIDDLEWARE_CLASSES
        for middleware_name in middlewares:
            middleware_class = load_class(middleware_name)
            middleware = middleware_class()
            if getattr(middleware, 'process_request', None):
                middleware.process_request(request)

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

        # add breadcrumbs to request
        for page_id, page_title in page.breadcrumbs:
            page_url = reverse('markup:page', kwargs={'id': page_id})
            request.breadcrumbs(page_title, page_url)


    def render_page(self, page, base_request=None):
        ''' Рендеринг страницы '''
        log = logging.getLogger('clever.markup')

        # Load template
        log.info("Load template from '%s' for page %s [%s]", page.template_name, page.id, page.title)
        template = page.load_template()

        # Load fixture
        log.info("Load fixture from '%s' for page %s [%s]", page.fixture_name, page.id, page.title)
        fixture = page.load_fixture()
        if fixture:
            try:
                log.error("Convert fixture from '%s' for page %s [%s]", page.fixture_name, page.id, page.title)
                fixture = self.fixture_factory.convert(fixture)
            except MetadataError as e:
                log.error("Convert fixture from '%s' for page %s [%s] is failed with error %s", page.fixture_name, page.id, page.title, e.message)
                e.message = "%s in '%s'" % (e.message, page.fixture_name)
                raise

        # Render template with fixture
        log.info("Rende page '%s' for page %s [%s]", page.fixture_name, page.id, page.title)
        request = self.request_factory.get(page.url)
        if base_request:
            request.GET = base_request.GET
            request.POST = base_request.POST
        context = RequestContext(request, fixture)
        self.prepare_page(page, request, context)
        return template.render(context)

    def render_index(self):
        template = loader.get_template('markup/index.jhtml')
        fixture = {
            'manager': self,
            'pages': self.pages,
        }
        return template.render(Context(fixture))
