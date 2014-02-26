from clever.markup.extensions.forms import FormExtension
from clever.markup.extensions.models import ModelExtension
from clever.markup.extensions.objects import ObjectExtension


class FixtureFactory(object):
    extensions = None

    def __init__(self):
        self.extensions = {
            '.model': ModelExtension(self),
            '.form': FormExtension(self),
            '.object': ObjectExtension(self),
        }

    def __getattr__(self, name):
        converter_id = '.' + name
        if converter_id in self.extensions:
            return self.extensions[converter_id]
        raise AttributeError("Not found converter %s in factory" % name)

    def get_metadata(self, converter_id, converter_name):
        if not converter_id in self.extensions:
            raise MetadataError('Not found metadata converter for data')
        return self.extensions[converter_id].get_metadata(converter_name)

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
                for converter_id, converter_name in descriptor.items():
                    if converter_id in self.extensions:
                        metadata = self.get_metadata(converter_id, converter_name)
                        del descriptor[converter_id]
                        break

                if not metadata:
                    raise MetadataError('Not found metadata for data')
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
