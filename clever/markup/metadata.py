from decimal import Decimal
from django.core.files import File

DEFAULT_TYPES = {
    'id': int,
    'url': unicode,
    'text': unicode,
    'price': Decimal,
    'file': File,
    'image': File
}

DEFAULT_FIELDS = {
    # Simple fields
    'id': 'int',
    'url': 'url',
    'title': 'text',
    'text': 'text',
    'image': 'image',
    'price': 'price',

    # Foreign fields
    'product': 'catalog.Product',
    'section': 'catalog.Section',
    'brand': 'catalog.Brand',
}


def get_metadata(value):
    if isinstance(value, dict):
        metadata = value.get('.metadata', None)
        if metadata:
            del value['.metadata']
            return metadata, value
    return None, value


class ModelFactory:
    name = None
    fields = None

    def __init__(self, params, name=None):
        self.name = name
        self.fields = {}
        # import ipdb; ipdb.set_trace() # BREAKPOINT

        for name, type in params.get('fields', {}).items():
            pass
            # id: int
            # url: url
            # title: text
            # text: text
            # section: catalog.Section
            # brand: catalog.Brand
            # image: image
            # price: price

    def update(self, params):
        pass

    def create(self, params):
        pass

class ModelManager:
    models = {}

    def __init__(self, name=None, metadata=None):
        pass

    def get_model_by_metadata(self, metadata):
        model_name = metadata.get('model')

        if not model_name:
            return ModelFactory(metadata)
        elif not model_name in self.models:
            self.models[model_name] = ModelFactory(metadata, name=model_name)
        return self.models[model_name]


class FixtureFactory:
    manager = None

    def __init__(self):
        self.manager = ModelManager()

    def get_model(self, metadata):
        return self.manager.get_model_by_metadata(metadata)

    def convert(self, value):
        return value
        metadata = None

        # tuple or list
        if isinstance(value, (list, tuple)):
            if len(value):
                metadata, value = get_metadata(value[0])

            if metadata:
                model = self.get_model(metadata)

                # Update model
                for item in value:
                    model.update(item)

                # Update metadata
                result = []
                for item in value:
                    result.append(model.create(item))
                return result
            else:
                result = []
                for item in value:
                    result.append(self.convert(item))
                return result

        # dictonary
        elif isinstance(value, dict):
            metadata, value = get_metadata(value)
            if metadata:
                model = self.get_model(metadata)
                return model.create(value)
            else:
                result = {}
                for key, item in value.items():
                    result[key] = self.convert(item)
                return result

        # original
        return value
