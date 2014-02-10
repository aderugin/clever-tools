# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from django.db.models import get_app_paths
from django.utils.functional import cached_property
from django.conf import settings
from django.utils._os import upath
import os
import codecs


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
            import yaml
            return yaml.load(file)
        elif fileext == '.json':
            import json
            return json.load(file, encoding)
        else:
            raise RuntimeError("Unknown loader for file %s" % filename)
    finally:
        file.close()
