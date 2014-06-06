# -*- coding: utf-8 -*-
import itertools
from clever.path import ensure_dir
from clever.process import ConsoleProcessLogger
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
        params = {
            code_name: id
        }
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
    title = None

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

            # Update statistics
            if is_updated:
                self.updated_count += 1
            elif is_deleted:
                self.deleted_count += 1
            else:
                self.created_count += 1

            #
            return instance
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
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


class AbstractManager(object):
    def __init__(self, parsers):
        self.parsers = []
        for ps in parsers:
            self.parsers.append(ElementManager.create(ps))

    def __iter__(self):
        """ Перебор всех элементов """
        return iter(self.parsers)

    def each(self):
        return self.parsers + sum(map(lambda parser: parser.each(), self.parsers), [])

    def get_parsers_count(self):
        return len(self.parsers) + sum(map(lambda parser: parser.get_parsers_count(), self.parsers))


class ElementManager(AbstractManager):
    parser = None
    _title = None

    def __init__(self, parser, parsers):
        super(ElementManager, self).__init__(parsers)
        self.parser = parser()

    @classmethod
    def create(cls, specification):
        """ Создание внутренней спецификации """
        if not isinstance(specification, (list, tuple)):
            specification = [specification, []]
        return cls(specification[0], specification[1])

    def get_elements_count(self, root):
        """ Получение количества элементов в XML файле """
        count = 0
        for item in root.iter(self.parser.item_tag_name):
            count += 1 + sum(map(lambda parser: parser.get_elements_count(item), self.parsers))
        return count

    @property
    def title(self):
        if not self._title:
            if self.parser.title:
                self._title = self.parser.title
            else:
                self._title = unicode(self.parser.model._meta.verbose_name_plural)
        return self._title

    def parse(self, root, logger, parent=None):
        self.parser.parent = parent
        for item in root.iter(self.parser.item_tag_name):
            instance = self.parser.process_item(item, parent)

            # notify progress
            logger += 1

            # parse subparsers
            for parser in self.parsers:
                parser.parse(item, logger, instance)
        self.parser.parent = None

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

    def summary(self, logger, width=0):
        if self.processed_count:
            # logger.notice(u"%s- Импортировано %d", u' ' * width, self.processed_count)
            if self.created_count:
                logger.notice(u"%s- Создано: %d", u' ' * width, self.created_count)
            if self.updated_count:
                logger.notice(u"%s- Обновлено: %d", u' ' * width, self.updated_count)
            if self.deleted_count:
                logger.notice(u"%s- Удалено: %d", u' ' * width, self.deleted_count)
            if self.errors_count:
                logger.notice(u"%s- Ошибок: %d", u' ' * width, self.errors_count)
        # else:
        #     logger.notice(u'%s- Нечего не импортировано',  u' ' * width)


class ImportManager(AbstractManager):
    """ Базовый класс для выполнения импорта """
    def __init__(self, parsers, progress=None):
        super(ImportManager, self).__init__(parsers)

        self.progress = progress or ConsoleProcessLogger()
        self.errors = []

    def get_elements_count(self, source):
        """ Подсчет кол-ва элементов """
        tree = etree.parse(source)
        return sum(map(lambda p: p.get_elements_count(tree), self))

    def parse(self, source):
        """ Актуальный парсер """
        # Импорт экземпляров моделей в базу
        count = self.get_parsers_count()
        index = 1
        tree = etree.parse(source)

        number_width = len(str(count))
        full_width = number_width * 2 + 2
        format = u'[%' + unicode(number_width) + u'd/%d] '

        for parser in self.parsers:
            # Импортируем экземпляры модели
            self.progress.info(format + u'Импорт элементов: %s', index, count, parser.title)
            parser.parse(tree, self.progress)
            index += 1
            parser.summary(self.progress, full_width)

            for subparser in parser.each():
                self.progress.info(format + u'Импорт элементов: %s', index, count, subparser.title)
                subparser.summary(self.progress, full_width)
                index += 1

            # Обновляем сатистику
            self.errors += parser.errors

            # Показать ошибки
            self.progress.show_errors(parser.errors)
            for subparser in parser.each():
                self.progress.show_errors(subparser.errors)

            # Очистка Garbage Collector'а
            gc.collect()

    def import_xml(self, name, store=False):
        filename = os.path.realpath(os.path.join(settings.PROJECT_DIR, '../cache', IMPORT_DIRECTORY, name))
        self.progress.info(u'Импорт файла: %s', filename)
        self.progress.line()

        # Проверка существования файла
        try:
            with open(filename) as source:
                # Поиск кол-ва элементов, если это требуется
                self.progress.initialize(self.get_elements_count(source))
                source.seek(0)

                # Импорт элементов из xml
                self.parse(source)
        except IOError:
            self.progress.error(u'Файл `%s` не найден', unicode(filename))
            return False
        else:
            # Удаляем файл файл в архив
            if not store:
                dt = str(datetime.datetime.now())
                new_name = 'import_' + dt.replace(' ', '_') + '.xml'
                directory = os.path.realpath(os.path.join(settings.PROJECT_DIR, '../cache', BACKUP_DIRECTORY))
                ensure_dir(directory)
                fullname = os.path.join(directory, new_name)
                os.rename(filename, fullname)
                self.progress.info(u"Перемещение файла: %s", fullname)

            # Вывод полной информации о импорте
            self.progress.line()
            self.progress.complete(u"Импорт завершен")
            return False
