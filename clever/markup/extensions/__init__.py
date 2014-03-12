# -*- coding: utf-8 -*-


class PageExtension(object):
    def __init__(self, factory):
        self.factory = factory

    def process_data(self, data):
        pass

    def process_page(self, page, request, context):
        raise NotImplementedError()


class FixtureExtension(object):
    factory = None

    def __init__(self, factory):
        self.factory = factory

    def get_metadata(self, model_name):
        raise NotImplementedError()

class FixtureMetadata(object):
    def update(self, descriptor):
        raise NotImplementedError()

    def convert(self, data):
        raise NotImplementedError()
