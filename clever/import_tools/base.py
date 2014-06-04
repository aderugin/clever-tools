# -*- coding: utf-8 -*-
from django.conf import settings
import sys
import os
from django.core.files import File
from django_importer.importers.xml_importer import XMLImporter as BaseXMLImporter
from lxml import etree
import gc
import datetime
from raven.contrib.django.models import get_client


IMPORT_DIRECTORY = 'exchange_1c/import'

BACKUP_DIRECTORY = 'backup/import'


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
        filepath = os.path.join(settings.PROJECT_DIR, '../cache', import_dir, file_dir, name)
        try:
            file = open(filepath, 'r')
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
    ignore_clear = []
    raven = None

    def __init__(self, source=None):
        super(XMLImporter, self).__init__(source)

        self.raven = get_client()
        self.errors = []
        self.errors_count = 0
        self.created_count = 0
        self.updated_count = 0
        self.processed_count = 0
        self.deleted_count = 0

    def is_delete_item(self, item, data, instance):
        return False

    def delete_item(self, item, data, instance):
        if instance.pk:
            instance.delete()

    def process_item(self, item, parent):
        data = None
        try:
            # Parse the fields from the source into a dict
            data = self.parse_item(item)

            # Get the instance from the DB, or a new one
            instance = self.get_instance(data)

            # Feed instance with data
            self.feed_instance(data, instance)

            # Save model instance
            is_updated = False
            is_deleted = False
            self.processed_count += 1

            if self.is_delete_item(item, data, instance):
                is_deleted = True
                if instance.pk:
                    self.deleted_count += 1
                    self.delete_item(item, data, instance)
            else:
                is_updated = not instance.pk is None
                self.save_item(item, data, instance)
                if is_updated:
                    self.updated_count += 1
                else:
                    self.created_count += 1
            return instance
        except KeyboardInterrupt:
            raise
        except Exception:
            try:
                err = sys.exc_info()
                verbose_name = self.model._meta.verbose_name_plural.title()
                if not data:
                    data = {}
                self.raven.captureException(err, import_model=self.model, import_name=verbose_name, import_parser=self, import_item=item, **data)
                self.save_error(data, err)
                self.errors_count += 1
            finally:
                del err

            return None


class ImportSpecification:
    parser = None

    def __init__(self, parser, subparsers):
        self.parser = parser()
        self.subparsers = []
        for ps in subparsers:
            self.subparsers.append(ImportSpecification.create(ps))

    def parse(self, root, instance=None):
        self._parse_iter(root.iter(self.parser.item_tag_name), instance)

    def _parse_iter(self, iter, instance):
        self.parser.parent = instance
        for item in iter:
            self_instance = self.parser.process_item(item, instance)

            for parser in self.subparsers:
                parser.parse(item, self_instance)
        self.parser.parent = None

    def progress_parse(self, root, instance=None):
        """
        Parses all data from the source, saving model instances.
        """
        def progressbar(items, prefix="", size=60):
            import itertools
            items, items_count = itertools.tee(items)
            count = len([x for x in items_count])

            if count:
                def _show(_i):
                    x = int(size*_i/count)
                    sys.stdout.write("%s[%s%s] %i/%i Ошибок: %i\r" % (prefix, "#" * x, "." * (size - x), _i, count, self.parser.errors_count))
                    sys.stdout.flush()

                _show(0)
                i = 0
                for item in items:
                    # item = items.pop(0)
                    yield item

                    # Unload item
                    item.clear()

                    # cleanup
                    if i % 1000:
                        gc.collect()

                    # Show progress
                    _show(i + 1)
                    i += 1
                sys.stdout.write("\n")
                sys.stdout.flush()
        self._parse_iter(progressbar(root.iter(self.parser.item_tag_name), "Прогресс: "), instance)

    @property
    def model(self):
        return self.parser.model

    @property
    def errors(self):
        return self.parser.errors

    @property
    def errors_count(self):
        return self.parser.errors_count

    @property
    def processed_count(self):
        return self.parser.processed_count

    @property
    def created_count(self):
        return self.parser.created_count

    @property
    def deleted_count(self):
        return self.parser.deleted_count

    @property
    def updated_count(self):
        return self.parser.updated_count

    @classmethod
    def create(cls, specification):
        if not isinstance(specification, (list, tuple)):
            specification = [specification, []]
        return cls(specification[0], specification[1])

    def each(self):
        result = [self]
        for parser in self.subparsers:
            result += parser.each()
        return result


class ImportFactory(object):
    ''' Базовый класс для выполнения импорта '''
    def __init__(self, parsers):
        self.errors = []
        self.parsers = []
        for ps in parsers:
            self.parsers.append(ImportSpecification.create(ps))

    def print_errors(self, errors=None):
        former_errors = set()
        if errors is None:
            errors = self.errors

        if len(errors):
            for error in errors:
                exception_message = '%s' % error['exception']
                if not exception_message in former_errors:
                    sys.stdout.write(''.join(["    - Информация об ошибке: \n\033[31m", exception_message, "\033[39m\n"]))
                    former_errors.add(exception_message)

    def parse(self, source, store=False):
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
        tree = etree.parse(filename)

        for parser in self.parsers:
            parsers.append(parser)
            model_verbose_name = parser.model._meta.verbose_name_plural.title()

            # Импортируем экземпляры модели
            print text_color(u'[', unicode(index), u'/', unicode(count), u"] Импорт элементов: ", unicode(model_verbose_name), color='green')
            parser.progress_parse(tree)

            # Обновляем сатистику
            self.errors += parser.errors

            for current in parser.each():
                model_verbose_name = current.model._meta.verbose_name_plural.title()
                print text_color(u'Импортировано ', unicode(model_verbose_name), ' ', unicode(current.processed_count), color='green')
                sys.stdout.write(''.join([
                    u"    - Создано: ", unicode(current.created_count),   "\n",
                    u"    - Обновлено: ", unicode(current.updated_count), "\n",
                    u"    - Удалено: ", unicode(current.deleted_count),   "\n",
                    u"    - Ошибок: ", unicode(current.errors_count),     "\n",
                ]))
                self.print_errors(current.errors)
            index += 1
            gc.collect()

        # Удаляем файл файл в архив
        if not store:
            dt = str(datetime.datetime.now())
            newname = 'import_' + dt.replace(' ', '_') + '.xml'
            os.rename(filename, os.path.join(settings.PROJECT_DIR, '../cache', BACKUP_DIRECTORY, newname))

        # Вывод полной информации о импорте
        print u'---------------------------------------------------------------'
        print text_color(u"Импорт завершен")
        return True
