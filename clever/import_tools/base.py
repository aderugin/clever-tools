# -*- coding: utf-8 -*-
from django.conf import settings
import sys
import codecs
import locale
import os
from django.core.files import File

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


def create_object_parser(model, tag_name):
    def parse_object(self, item, field_name, source_name):
        return model.objects.get(code=item.get(tag_name).strip())
    return parse_object


def create_image_parser(tag_name, import_dir='exchange_1c/import/images'):
    def get_image(self, name):
        """
        If image exist return file
        """
        file_path = os.path.join(settings.PROJECT_DIR, '../cache', import_dir, name)
        try:
            image = open(file_path, 'r')
            if image is not None:
                return File(image, name)
        except:
            pass
        return None

    def parse_image(self, item, field_name, source_name):
        value = item.get(tag_name, None)
        if value:
            return get_image(self, value)
        return None

    return parse_image


class ImportFactory:
    def __init__(self):
        self.parsers = []

    def append(self, cls):
        self.parsers.append(cls)

    def parse(self, source):
        for cls in self.parsers:
            parser = cls(source)
            model_verbose_name = parser.model._meta.verbose_name_plural.title()
            print u"Импорт элементов: ", model_verbose_name
            parser.parse()
        print u"Импорт завершен"
