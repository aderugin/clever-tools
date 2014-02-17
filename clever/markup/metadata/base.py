from . import fields
from decimal import Decimal
from django.db import models
from clever.magic import load_class

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
    'django.db.models.fields.files.FileField':     fields.FileConverter(),

    # Self converters
    'mptt.fields.TreeForeignKey':                   fields.ForeignConverter(),
    'django.db.models.fields.related.ForeignKey':   fields.ForeignConverter()
}


def get_type_fullname(o):
    return o.__module__ + "." + o.__class__.__name__


class MetadataError(Exception):
    pass


class Metadata(object):
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

        # create model metadata
        class Meta(object):
            app_label = None
        Meta.app_label = app_name

        # create bases for model class
        name = '%s.%s' % (app_name, model_name)
        bases = (models.Model,)
        if name in DEFAULT_PARENTS:
            bases= (load_class(DEFAULT_PARENTS[name]),)

        # create model class
        if not model_class:
            model_class = type(model_name, bases, {'__module__': app_name, 'Meta': Meta})
        self.model_class = model_class

        # auto recreate existed members
        for field in self.model_class._meta.fields:
            type_name = get_type_fullname(field)
            converter = INVERT_FIELDS.get(type_name, None)
            if converter:
                self.update_field(field.name, converter=converter.recreate(self.factory, self, field))

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
                field = models.CharField(max_length=255)

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
        instance = self.model_class()
        for key, value in data.items():
            if key in self.fields:
                value = self.fields[key].convert(self.factory, instance, data, value)
            setattr(instance, key, value)
        return instance


class FixtureFactory(object):
    models = {}

    def __init__(self):
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
            metadata = Metadata(self, app_name, model_name, model_class)
            self.models[name] = metadata
        return metadata

    def find_metadata(self, value):
        ''' Find and create metadata '''
        if isinstance(value, (list, tuple)) and len(value) > 0:
            metadata, skip_value = self.find_metadata(value[0])
            if metadata:
                value = list(value)
                value.pop(0)
                return metadata, value
        elif isinstance(value, dict):
            descriptor = value.get('.metadata', None)
            if isinstance(descriptor, dict):
                del value['.metadata']
                model_name = descriptor.get('.model', None)
                del descriptor['.model']
                metadata = self.get_metadata(model_name)
                metadata.update(descriptor)
                return metadata, value
        return None, value

    def convert(self, value):
        metadata, value = self.find_metadata(value)
        if metadata:
            if isinstance(value, (list, tuple)):
                result = []
                for x in value:
                    result.append(metadata.convert(x))
                return result
            elif isinstance(value, dict):
                return metadata.convert(value)
        elif isinstance(value, (list, tuple)):
            result = []
            for x in value:
                result.append(self.convert(x))
            return result
        elif isinstance(value, dict):
            result = {}
            for k, x in value.items():
                result[k] = self.convert(x)
            return result
        return value
