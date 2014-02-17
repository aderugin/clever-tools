# -*- coding: utf-8 -*-
from decimal import Decimal
from django.db import models
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.files.images import ImageFile
from django.contrib.staticfiles.finders import find


class FieldConverter(object):
    def create_field(self, factory, name, param):
        raise NotImplementedError()

    def convert(self, factory, instance, data, value):
        return value

    def recreate(self, factory, base_metadata, field):
        raise NotImplementedError()


class FileConverter(FieldConverter):
    def create_field(self, factory, name, param):
        return models.FileField(verbose_name=u'Файл')

    def convert(self, factory, instance, data, filename):
        return File(open(find(filename)), name=filename)

    def recreate(self, factory, base_metadata, field):
        return self


class ImageConverter(FieldConverter):
    def create_field(self, factory, name, param):
        return models.ImageField(verbose_name=u'Изображение')

    def convert(self, factory, instance, data, filename):
        return ImageFile(open(find(filename)), name=filename)

    def recreate(self, factory, base_metadata, field):
        return self


class UrlConverter(FieldConverter):
    PREFIX_URL = 'markup:'
    PREFIX_SIZE = len(PREFIX_URL)

    def create_field(self, factory, name, param):
        return models.URLField(verbose_name=u'URL страницы')

    def convert(self, factory, instance, data, value):
        if value.startswith(self.PREFIX_URL):
            return reverse('markup:page', kwargs={'id': value[self.PREFIX_SIZE:]})
        return value

    def recreate(self, factory, base_metadata, field):
        return self


class DecimalConverter(FieldConverter):
    def create_field(self, factory, name, param):
        return models.DecimalField(verbose_name=u'Цена')

    def convert(self, factory, instance, data, value):
        return Decimal(value)

    def recreate(self, factory, base_metadata, field):
        return self


class ForeignConverter(FieldConverter):
    model_name = None

    def __init__(self, model_name=None):
        self.model_name = model_name

    def create_field(self, factory, name, param):
        if not self.model_name:
            raise RuntimeError('ForeignConverter has not model name')
        metadata = factory.get_metadata(self.model_name)
        return models.ForeignKey(metadata.model_class)

    def convert(self, factory, instance, data, value):
        if not self.model_name:
            raise RuntimeError('ForeignConverter has not model name')

        if value:
            metadata = factory.get_metadata(self.model_name)
            return metadata.convert(value)
        return None

    def recreate(self, factory, base_metadata, field):
        rel_model = field.rel.to
        if base_metadata.model_class == rel_model:
            return ForeignConverter("%s.%s" % (base_metadata.app_name, base_metadata.model_name))

        for name, metadata in factory.models.items():
            if metadata.model_class == rel_model:
                return ForeignConverter(name)

        raise RuntimeError('Not found metadata for model in foreign key %s' % rel_model.__class__)
