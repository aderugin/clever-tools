# -*- coding: utf-8 -*-
from django.conf import settings

from django.template import loader
from django.template import Context
from django.template import RequestContext

from django.test.client import RequestFactory

from django.core.urlresolvers import reverse

from clever.markup.extensions.breadcrumbs import BreadcrumbsExtension
from clever.markup.extensions.paginator import PaginatorExtension
from clever.markup.extensions.cart import CartExtension
from clever.markup.extensions.compare import CompareExtension

from clever.markup.metadata import fixture_factory
from clever.markup.metadata import MetadataError

from clever.fixture import load_fixture
from clever.fixture import FixtureNotFound

from clever.magic import load_class

from collections import OrderedDict

import logging
import os


class Page(object):
    id = None
    title = None
    params = None

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

    def __getattr__(self, name, default=None):
        return self.params.get(name, default)


class Manager(object):
    extensions = None
    fixture_factory = None
    request_factory = None
    pages = None

    def __init__(self, fixture_name='markup.yaml'):
        self.extensions = [
            BreadcrumbsExtension(),
            PaginatorExtension(),
            CartExtension(),
            CompareExtension(),
        ]
        self.request_factory = RequestFactory(SERVER_NAME="localhost")
        self.fixture_factory = fixture_factory
        self.pages = OrderedDict()

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

        # run page extensions
        for extension in self.extensions:
            extension.process_page(page, request, context)


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
