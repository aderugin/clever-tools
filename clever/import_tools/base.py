# -*- coding: utf-8 -*-
from django.conf import settings
import sys
import os
from django.core.files import File
from django_importer.importers.xml_importer import XMLImporter as BaseXMLImporter
from django_importer.importers.xml_importer import ElementTree


IMPORT_DIRECTORY = 'exchange_1c/import'


def create_object_parser(model, tag_name, code_name='code', required=False):
    ''' Создание типа для объекта '''
    def parse_object(self, item, field_name, source_name):
        id = item.get(tag_name, '').strip()
        params = {code_name: id}
        try:
            return model.objects.get(**params)
        except model.DoesNotExist, e:
            if required:
                raise e
            return None
    return parse_object


def create_file_parser(tag_name, import_dir=IMPORT_DIRECTORY, file_dir='', required=False):
    def get_file(self, name):
        """
        If file exist return file
        """
        file_path = os.path.join(settings.PROJECT_DIR, '../cache', import_dir, file_dir, name)
        print file_path
        try:
            file = open(file_path, 'r')
            if file is not None:
                return File(file, name)
        except:
            if required:
                raise
        return None

    def parse_file(self, item, field_name, source_name):
        value = item.get(tag_name, None)
        if value:
            return get_file(self, value)
        elif required:
            raise RuntimeError('Not found file')
        return None

    return parse_file


class XMLImporter(BaseXMLImporter):
    def __init__(self, source=None):
        super(XMLImporter, self).__init__(source)

        self.element_count = 0
        self.created_count = 0
        self.updated_count = 0
        self.errors_count = 0
        self.processed_count = 0

    def get_items(self):
        """
        Iterator of the list of items in the XML source.
        """
        # Use `iterparse`, it's more efficient, specially for big files
        for event, item in ElementTree.iterparse(self.source):
            if item.tag == self.item_tag_name:
                yield item

    def parse(self):
        def progressbar(items, prefix="", size=60):
            items = [x for x in items]
            count = len(items)

            if count:
                def _show(_i):
                    x = int(size*_i/count)
                    sys.stdout.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), _i, count))
                    sys.stdout.flush()

                _show(0)
                for i, item in enumerate(items):
                    yield item
                    _show(i+1)
                sys.stdout.write("\n")
                sys.stdout.flush()

        """
        Parses all data from the source, saving model instances.
        """
        # Checks if the source is loaded
        if not self.loaded:
            self.load(self.source)

        for item in progressbar(self.get_items(), "Прогресс: "):
            self.element_count += 1
            data = {}

            try:
                # Parse the fields from the source into a dict
                data = self.parse_item(item)

                # Get the instance from the DB, or a new one
                instance = self.get_instance(data)

                # Feed instance with data
                self.feed_instance(data, instance)

                # Save model instance
                is_updated = not instance.pk is None
                self.save_item(item, data, instance)

                # Update info about models
                self.processed_count += 1
                if is_updated:
                    self.updated_count += 1
                else:
                    self.created_count += 1
            except Exception, e:
                self.errors_count += 1
                self.save_error(data, sys.exc_info())

        # Unload the source
        self.unload()


class ImportFactory(object):
    ''' Базовый класс для выполнения импорта '''
    def __init__(self):
        self.parsers = []
        self.errors = []

    def append(self, cls):
        self.parsers.append(cls)

    def print_errors(self, errors=None):
        former_errors = set()

        if len(self.errors):
            for error in self.errors:
                exception_message = '%s' % error['exception']
                if not exception_message in former_errors:
                    sys.stdout.write(''.join(["    Ошибка: \033[31m", exception_message, "\033[39m\n"]))
                    former_errors.add(exception_message)

    def parse(self, source):
        def text_color(*args, **kwargs):
            color = kwargs.get('color', 'green')
            string = u''.join(args)
            if color == 'red':
                return '\033[31m' + string + '\033[39m'
            return '\033[32m' + string + '\033[39m'

        filename = os.path.join(settings.PROJECT_DIR, '../cache', IMPORT_DIRECTORY, source)
        print u'Импорт файла:', filename
        try:
            with open(filename):
                pass
        except IOError:
            u'Файл `%s` не найден' % unicode(filename)
            return False

        # Импорт экземпляров моделей в базу
        count = len(self.parsers)
        index = 1
        parsers = []
        for cls in self.parsers:
            parser = cls(filename)
            parsers.append(parser)
            model_verbose_name = parser.model._meta.verbose_name_plural.title()

            # Импортируем экземпляры модели
            print text_color(u'[', unicode(index), u'/', unicode(count), u"] Импорт элементов: ", unicode(model_verbose_name), color='green')
            parser.parse()

            # Обновляем сатистику
            self.errors += parser.errors
            sys.stdout.write(''.join([
                u"    Успешно обработано: ", unicode("%s/%s" % (parser.processed_count, parser.element_count)), "\n"
            ]))
            sys.stdout.write(''.join([
                u"    Создано: ", unicode(parser.created_count),
                u". Обновлено: ", unicode(parser.updated_count), "\n"
            ]))
            self.print_errors(parser.errors)
            index += 1

        # Вывод полной информации о импорте
        print u'---------------------------------------------------------------'
        print text_color(u"Импорт завершен")
        for parser in parsers:
            model_verbose_name = parser.model._meta.verbose_name_plural.title()
            print text_color(u'Импортировано ', unicode(model_verbose_name), ' ', unicode(parser.processed_count), u' из ', unicode(parser.element_count), color='green')
        return True
