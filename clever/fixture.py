# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from django.db.models import get_app_paths
from django.utils.functional import cached_property
from django.conf import settings
from django.utils._os import upath
from collections import OrderedDict
import os
import codecs
import yaml
import json

class OrderedDictYAMLLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

# TODO: Разбор из данных Yaml в модели Django
class FixtureNotFound(Exception):
    pass


class FixtureLoader(object):
    @cached_property
    def fixture_dirs(self):
        """
        Return a list of fixture directories.

        The list contains the 'fixtures' subdirectory of each installed
        application, if it exists, the directories in FIXTURE_DIRS, and the
        current directory.
        """
        dirs = []
        for path in get_app_paths():
            d = os.path.join(os.path.dirname(path), 'fixtures')
            if os.path.isdir(d):
                dirs.append(d)
        dirs.extend(list(settings.FIXTURE_DIRS))
        dirs.append('')
        dirs = [upath(os.path.abspath(os.path.realpath(d))) for d in dirs]
        return dirs

    def find_fixture(self, filename, encoding):
        dirs = self.fixture_dirs

        for path in dirs:
            fullname = os.path.join(path, filename)
            try:
                return codecs.open(fullname, 'r', 'utf-8')
            except IOError, e:
               pass

        raise FixtureNotFound('Fixture %s not found in project' % (filename))


loader = FixtureLoader()
def load_fixture(filename, encoding='utf-8'):
    ''' Load fixture data from file '''
    file = loader.find_fixture(filename, encoding)
    try:
        (fileroot, fileext) = os.path.splitext(filename)
        if fileext == '.yaml':
            return yaml.load(file, OrderedDictYAMLLoader)
        elif fileext == '.json':
            return json.load(file, encoding)
        else:
            raise RuntimeError("Unknown loader for file %s" % filename)
    finally:
        file.close()
