# -*- coding: utf-8 -*-


class PageExtension(object):
    def process_page(self, page, request, context):
        raise NotImplementedError()


class FixtureExtension(object):
    factory = None

    def __init__(self, factory):
        self.factory = factory

    def get_metadata(self, model_name):
        raise NotImplementedError()

    def update(self, descriptor):
        raise NotImplementedError()
