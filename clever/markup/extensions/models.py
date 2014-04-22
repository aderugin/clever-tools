# -*- coding: utf-8 -*-
from decimal import Decimal
from django.db import models
from django.db.models.loading import get_model
from django.core.urlresolvers import reverse
from clever.magic import load_class
from clever.markup.metadata import fields
from clever.markup.metadata import MetadataError
from clever.markup.extensions import FixtureExtension
from clever.markup.extensions import FixtureMetadata


DEFAULT_FIELDS = {
    # Simple fields
    'url':          fields.UrlConverter(),
    # File fields
    'file':         fields.FileConverter(),
    'image':        fields.ImageConverter(),

    # Price fields
    'price':        fields.DecimalConverter(),
    'old_price':    fields.DecimalConverter(),
    'new_price':    fields.DecimalConverter(),

    # Foreign fields
    'product':      fields.ForeignConverter('catalog.product'),
    'section':      fields.ForeignConverter('catalog.section'),
    'brand':        fields.ForeignConverter('catalog.brand'),
}

DEFAULT_PARENTS = {
    'pages.page':       'clever.pages.models.Page',
    'catalog.product':  'clever.catalog.models.ProductBase',
    'catalog.section':  'clever.catalog.models.SectionBase',
    'catalog.brand':    'clever.catalog.models.BrandBase',
}

INVERT_FIELDS = {
    'django.db.models.fields.files.ImageField':     fields.ImageConverter(),
    'django.db.models.fields.files.FileField':      fields.FileConverter(),

    # Self converters
    'mptt.fields.TreeForeignKey':                   fields.ForeignConverter(),
    'django.db.models.fields.related.ForeignKey':   fields.ForeignConverter()
}

def get_type_fullname(o):
    return o.__module__ + "." + o.__class__.__name__


class ModelExtension(FixtureExtension):
    models = None

    def __init__(self, factory):
        super(ModelExtension, self).__init__(factory)
        self.models = {}

    def get_metadata(self, name, model_class=None):
        metadata = self.models.get(name, None)
        if not metadata:
            # Find model name
            if not name:
                raise MetadataError(u"Model name must be in form `app_name.model_name` [%s]" % name)
            names = name.split('.')
            if len(names) != 2:
                raise MetadataError(u"Model name must be in form `app_name.model_name` [%s]" % name)
            app_name, model_name = names

            # Create metadata
            metadata = ModelMetadata(self, app_name, model_name, model_class)
            self.models[name] = metadata
        return metadata

    def __iter__(self):
        return iter(self.models.items())


class ModelMetadata(FixtureMetadata):
    app_name = None
    model_name = None
    model_class = None
    fields = None
    factory = None

    def __init__(self, factory, app_name, model_name, model_class=None):
        self.factory = factory
        self.app_name = app_name
        self.model_name = model_name
        self.fields = {}

        fix_name = 'fix-' + app_name

        # create bases for model class
        name = '%s.%s' % (app_name, model_name)
        bases = (models.Model,)

        is_proxy = False
        parent_model = get_model(app_name, model_name)
        if parent_model:
            is_proxy = True
            bases = (parent_model, )
        elif name in DEFAULT_PARENTS:
            is_proxy = True
            parent_model = load_class(DEFAULT_PARENTS[name])
            bases = (parent_model,)

        # if parent_model and not getattr(parent_model, '_base_manager', None):
        #     manager = models.Manager()
        #     manager.model = parent_model
        #     setattr(parent_model, '_base_manager', manager)

        # create model metadata
        class Meta(object):
            app_label = None
        Meta.proxy = is_proxy
        Meta.app_label = fix_name

        # create model class
        if not model_class:
            model_class = type(model_name, bases, {'__module__': fix_name, 'Meta': Meta, 'deferred_proxy': True})
        self.model_class = model_class

        # auto recreate existed members
        for field in self.model_class._meta.fields:
            type_name = get_type_fullname(field)
            converter = INVERT_FIELDS.get(type_name, None)
            if converter:
                self.update_field(field.name, converter=converter.recreate(self.factory, self, field, defaults=DEFAULT_PARENTS))

    def update(self, descriptor):
        for key, param in descriptor.items():
            self.update_field(key, param)

    def update_field(self, name, param=None, converter=None):
        # if field exists in current metadata return
        if self.fields.get(name, None):
            return

        # fill default params for field
        if not converter:
            if name in DEFAULT_FIELDS:
                converter = DEFAULT_FIELDS[name]
                field = converter.create_field(self.factory, name, param)
            else:
                # field = models.CharField(max_length=255)
                return

        # push converter to dict
        if converter:
            self.fields[name] = converter

        # if field exists
        equal_fields = any(f.name == name for f in self.model_class._meta.fields)

        # contribute to model if required
        if not equal_fields and field:
            field.contribute_to_class(self.model_class, name)

    def convert(self, data):
        # update model class
        for name, value in data.items():
            self.update_field(name)

        # create instance of model class
        # try:
        instance = self.model_class()
        # except Exception, e:
        #     import ipdb; ipdb.set_trace()

        for key, value in data.items():
            if key in self.fields:
                value = self.fields[key].convert(self.factory, instance, data, value)
            else:
                value = self.factory.factory.convert(value)
            setattr(instance, key, value)
        return instance
