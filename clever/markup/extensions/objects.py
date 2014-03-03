# -*- coding: utf-8 -*-
from clever.markup.metadata import MetadataError
from clever.markup.extensions import FixtureExtension
from clever.markup.extensions import FixtureMetadata


class Object(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs


class ObjectExtension(FixtureExtension):
    objects = None

    def __init__(self, factory):
        super(ObjectExtension, self).__init__(factory)
        self.objects = {}

    def get_metadata(self, name, model_class=None):
        metadata = self.objects.get(name, None)
        if not metadata:
            # Find model name
            if not name:
                raise MetadataError(u"Object name must be in form `object_name` [%s]" % name)

            # Create metadata
            metadata = ObjectMetadata(self, model_class)
            self.objects[name] = metadata
        return metadata

    def __iter__(self):
        return iter(self.objects.items())


class ObjectMetadata(FixtureMetadata):
    factory = None
    model_name = None

    def __init__(self, factory, model_name):
        self.factory = factory
        self.model_name = model_name

    def convert(self, data):
        factory = self.factory.factory
        result = {}
        for key, value in data.items():
            result[key] = factory.convert(value)
        return Object(**result)
