# -*- coding: utf-8 -*-
"""
:mod:`clever.catalog.models` -- Модели базового каталога
===================================

В данном модуле хранится базовый набор моделей для работы с каталогом.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
.. moduleauthor:: Семен Пупков <semen.pupkov@gmail.com>
"""

from django_importer.importers.xml_importer import XMLImporter
import datetime
import os
from django.conf import settings
import sys, codecs, locale;
sys.stdout = codecs.getwriter('utf8')(sys.stdout);

def die(msg):
    print msg
    raise SystemExit


helpers = (
    {
        'title': u'Импорт брэндов',
        'tag_name': 'Brend',   # tag in xml
        'model': PrumaCatalogBrand,  # model name
        'field_name_in_model': 'brand',  # field name in model to link
        'tag_name_id': 'BrendID',  # ID in xml
    },
    # {
    #     'tag_name': 'Action',
    #     'model': PrumaCatalogAction,
    #     'field_name_in_model': 'action',
    #     'tag_name_id': 'ActionID'
    # },
    {
        'title': u'Импорт возврата товаров',
        'tag_name': 'VozvratTovara',
        'model': PrumaCatalogReturn,
        'field_name_in_model': 'return_type',
        'tag_name_id': 'VozvratTovaraID'

    },
    {
        'title': u'Импорт демонстраций',
        'tag_name': 'Demonstration',
        'model': PrumaCatalogDemonstration,
        'field_name_in_model': 'demonstration',
        'tag_name_id': 'DemonstrationID'
    },
    {
        'title': u'Импорт доступности товаров',
        'tag_name': 'Dostupnost',
        'model': PrumaCatalogAvailable,
        'field_name_in_model': 'available',
        'tag_name_id': 'DostupnostID'
    },
    {
        'title': u'Импорт принадлежностей товара',
        'tag_name': 'Prinadleznost',
        'model': PrumaCatalogAccess,
        'field_name_in_model': 'access',
        'tag_name_id': 'PrinadleznostID'
    },
    {
        'title': u'Импорт типов товаров',
        'tag_name': 'TovarType',
        'model': PrumaCatalogItemType,
        'field_name_in_model': 'item_type',
        'tag_name_id': 'TovarTypeID'
    },
)


def parse_name(self, item, field_name, source_name):
    return item.get('Name').strip()


def parse_code(self, item, field_name, source_name):
    return item.get('ID').strip()


def parse_helper(self, item, field_name, source_name):
    for h in helpers:
        if h.get('field_name_in_model') == field_name:
            code_value = item.get(h.get('tag_name_id')).strip()
            if code_value:
                item = h.get('model').objects.get(code=code_value)
                if (item):
                    return item


class PrumaCatalogItemImporter(XMLImporter):
    """ Импортирует товары """

    model = PrumaCatalogItem

    item_tag_name = 'Tovar'

    fields = ('name', 'code', 'articul', 'price',
              'brand', 'access', 'available',
              'return_type', 'item_type',
              'demonstration', 'active', 'mark_for_delete',
              'units')

    unique_fields = ('code',)

    parse_name = parse_name
    parse_code = parse_code

    def parse_active(self, item, field_name, source_name):
        """ Проверка на передачу свойств деактиировать и на удаление """
        deactivate = 0

        if item.get('Deactivate'):
            deactivate = int(item.get('Deactivate'))

        if deactivate == 1:
            return False
        else:
            return True

    def parse_mark_for_delete(self, item, field_name=None, source_name=None):
        """ Проверка товара на удаление """
        mark_for_delete = 0

        if item.get('MarkForDelete'):
            mark_for_delete = int(item.get('MarkForDelete'))

        if mark_for_delete == 1:
            return True
        else:
            return False

    def parse_articul(self, item, field_name, source_name):
        return item.get('Articul').strip()

    def parse_price(self, item, field_name, source_name):
        return item.get('Price')

    def parse_category(self, item, field_name=None, source_name=None):
        category_code = item.get('ParentID').strip()

        if category_code:
            try:
                return (Category.objects.get(code=category_code),)
            except Category.DoesNotExist:
                pass
            pass

    def parse_action(self, item, field_name=None, source_name=None):
        action_code = item.get('ActionID').strip()

        if action_code:
            try:
                return PrumaCatalogAction.objects.get(code=action_code)
            except PrumaCatalogAction.DoesNotExist:
                pass
            pass

    def parse_units(self, item, field_name=None, source_name=None):
        return item.get('EdIzm')

    def save_item(self, item, data, instance, commit=True):
        """
        Saves a model instance to the database.
        """
        if commit:
            instance.save()

        category = self.parse_category(item)
        if category:
            instance.category = category
            #instance.save()

        action = self.parse_action(item)

        for action_item in PrumaCatalogActionItem.objects.filter(item__id=instance.id):
            action_item.delete()

        if action:
            try:
                action_item = PrumaCatalogActionItem(item=instance, action=action)
                action_item.save()

            except Exception, e:
                pass

        # # Если товар помечен на удалении - деативируем его
        # mark_for_delete = self.parse_mark_for_delete(item)
        # if mark_for_delete == True:
        #     instance.active = 0
        return instance

    # Привязки к справочникам
    parse_brand = parse_helper
    parse_access = parse_helper
    parse_available = parse_helper
    parse_return_type = parse_helper
    parse_item_type = parse_helper
    parse_demonstration = parse_helper


class PrumaCatalogCategoryImporter(XMLImporter):
    """ Импортирует категории """

    model = Category

    item_tag_name = 'Parent'
    fields = ('name', 'code',)
    unique_fields = ('code', )

    parse_name = parse_name
    parse_code = parse_code

    def parse_parent(self, item, field_name, source_name):

        item_code = item.get('ParentID')
        item_code = item_code.strip()
        if item_code:
            try:
                return Category.objects.get(code=item_code)
            except Category.DoesNotExist:
                pass
            pass


class PrumaRestImporter(XMLImporter):
    fields = ('product', 'whouse', 'count', )
    model = PrumaCatalogWarehouseCount
    unique_fields = ('product', 'whouse', )
    item_tag_name = 'Rest'

    def parse_product(self, item, field_name, source_name):
        item_code = item.get('TovarID').strip()

        if item_code:
            try:
                return PrumaCatalogItem.objects.get(code=item_code)
            except PrumaCatalogItem.DoesNotExist:
                pass
            pass

    def parse_whouse(self, item, field_name, source_name):
        whouse_code = item.get('WHouseID')

        if whouse_code:
            try:
                return PrumaCatalogWarehouse.objects.get(code=whouse_code)
            except PrumaCatalogWarehouse.DoesNotExist:
                pass
            pass

    def parse_count(self, item, field_name, source_name):
        return item.get('Kol') or 0


class PrumaCatalogHelperImporter(XMLImporter):
    fields = ('name', 'code',)
    unique_fields = ('code',)

    parse_name = parse_name
    parse_code = parse_code


def import_1c_catalog(source_file='goods.xml'):
    """ Выполняет процесс импортирования каталога """

    file_path = settings.MEDIA_ROOT + '/' + source_file

    if not os.path.isfile(file_path):
        print u"Файл для импорта не найден"
        return

    #Справочники
    helper_importer = PrumaCatalogHelperImporter(source=file_path)
    for h in helpers:
        print h.get('title')
        helper_importer.model = h.get('model')
        helper_importer.item_tag_name = h.get('tag_name')
        helper_importer.parse()

    # Склады
    print u"Импорт складов"
    helper_importer.model = PrumaCatalogWarehouse
    helper_importer.item_tag_name = 'WHouse'
    helper_importer.parse()

    # Категории
    print u"Импорт категории"
    categoy_importer = PrumaCatalogCategoryImporter(source=file_path)
    categoy_importer.parse()

    # Товары
    print u"Импорт товаров"
    item_importer = PrumaCatalogItemImporter(source=file_path)
    item_importer.parse()

    # Обновляем остатки
    print u"Импорт обновляем остатки"
    rest_importer = PrumaRestImporter(source=file_path)
    rest_importer.parse()

    # Удаляем файл файл в архив
    #os.remove(file_path)
    dt = str(datetime.datetime.now())
    newname = 'import_' + dt.replace(' ', '_') + '.xml'
    os.rename(file_path, os.path.join(settings.IMPORT_BACKUP_DIRECTORY, newname))
