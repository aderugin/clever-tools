# -*- coding: utf-8 -*-
from django.template import loader
from django.template import Context
from django.template import RequestContext
from django.test.client import RequestFactory
from clever.markup.metadata import FixtureFactory
from clever.fixture import load_fixture
from clever.fixture import FixtureNotFound
import yaml
import os
import codecs
import logging


class Page:
    id = None
    title = None
    params = None

    def __init__(self, id, title, params):
        self.id = id
        self.title = title
        self.params = params

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
        return self.params.get('url', '/' + self.id + '/')

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
        self.fixture_factory = FixtureFactory()
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

    def render_page(self, page):
        ''' Рендеринг страницы '''
        log = logging.getLogger('clever.markup')

        # Load template
        log.info("Load template from '%s' for page %s [%s]", page.template_name, page.id, page.title)
        template = page.load_template()

        # Load fixture
        log.info("Load fixture from '%s' for page %s [%s]", page.fixture_name, page.id, page.title)
        fixture = page.load_fixture()
        if fixture:
            fixture = self.fixture_factory.convert(fixture)

        # Render template with fixture
        log.info("Rende page '%s' for page %s [%s]", page.fixture_name, page.id, page.title)
        request = self.request_factory.get(page.url)
        context = RequestContext(request, fixture)
        return template.render(context)

    def render_index(self):
        template = loader.get_template('markup/index.jhtml')
        fixture = {
            'manager': self,
            'pages': self.pages,
        }
        return template.render(Context(fixture))
