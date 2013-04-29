# -*- coding: utf-8 -*-
"""
:mod:`clever.core.models` -- Ядро для работы с моделями
===================================

.. moduleauthor:: Семен Пупков (semen.pupkov@gmail.com)
.. moduleauthor:: Василий Шередеко (piphon@gmail.com)
"""
from django.db import models
from django.db.models import query
from hashlib import md5
from time import time
from model_utils import managers
from model_utils import fields
from caching import base as cache_machine
import autoslug
import os
from clever import magic


def generate_upload_name(instance, filename, prefix=None, unique=False):
    """
    Авто генерация имени для файлов и изображений, загруженных с помощью  FileField и ImageField.

    .. sectionauthor:: Семен Пупков (semen.pupkov@gmail.com)
    """
    if instance is None:
        return filename

    ext = os.path.splitext(filename)[1]
    name = str(instance.pk or '') + '-' + filename + '-' + (str(time()) if unique else '')

    # We think that we use utf8 based OS file system
    filename = md5(name.encode('utf8')).hexdigest() + ext
    basedir = os.path.join(instance._meta.app_label, '-', instance._meta.module_name)
    if prefix:
        basedir = os.path.join(basedir, prefix)
    return os.path.join(basedir, filename[:2], filename[2:4], filename)


class TimestableMixin(models.Model):
    """
    Миксин для добавления данных об дате создания и изменения
    """
    class Meta:
        abstract = True
    created_at = fields.AutoCreatedField(verbose_name=u'Дата создания')
    updated_at = fields.AutoLastModifiedField(verbose_name=u'Дата обновления')


class ActivableMixin(models.Model):
    """
    Миксин для добавления данных об дате создания и изменения
    """
    class Meta:
        abstract = True
    active = models.BooleanField(verbose_name=u'Активность', default=True)


class ActivableQuerySet(query.QuerySet):
    """
    Запрос для получение активных и неактивных объектов из БД
    """
    def active(self):
        """Фильтровать активные элементы"""
        return self.filter(active=True)

    def deactive(self):
        """Фильтровать неактивные элементы"""
        return self.filter(active=False)


class TitleMixin(models.Model):
    """
    Миксин для добавления данных об текстового заголовка и сегмента ЧПУ по этому
    заголовку
    """
    class Meta:
        abstract = True
    title = models.CharField(verbose_name=u"Название", max_length=255)
    # TODO: , editable=True - в админке при создании нового элемента, не срабатывает autopopulate
    slug = autoslug.AutoSlugField(verbose_name=u"ЧПУ сегмент", populate_from='title', sep='-', unique=True)

    # @models.permalink
    # def get_absolute_url(self):
    #     """
    #     Получение каноничного пути до раздела каталога
    #     """
    #     return (magic.get_meta_param(self, 'url_name'), (), {'slug': self.slug})

    def __unicode__(self):
        return self.title


class TitleQuerySet(query.QuerySet):
    """
    Запрос для получение активных и неактивных объектов из БД
    """
    def by_slug(self, slug):
        """Фильтровать активные элементы"""
        return self.filter(slug=slug)


class PageMixin(models.Model):
    """
    Миксин для добавления данных об тексте и изображении для страницы
    """
    class Meta:
        abstract = True
    image = models.ImageField(upload_to=generate_upload_name, verbose_name=u'Изображение', null=True, blank=True)
    text = models.TextField(verbose_name=u'Описание', blank=True)


class CachingPassThroughManager(managers.PassThroughManager, cache_machine.CachingManager):
    pass


class DeferredPoint(object):
    '''
    Базовый класс для предоставления создания 'отложенных точек' - абстрактных моделей
    для последующего использования в проектах
    '''
    def __init__(self):
        self.__dict__['__consumers'] = []

    def resolve_deferred_point(self, target_model):
        self.__dict__['__instance'] = target_model
        for consumer in self.__dict__['__consumers']:
            consumer.resolve_deferred_point(target_model)

    def connect_deferred_consumer(self, consumer):
        self.__dict__['__consumers'].append(consumer)

    def __getattr__(self, name):
        return getattr(self.__dict__['__instance'], name)

    def __setattr__(self, name, value):
        return setattr(self.__dict__['__instance'], name, value)


class DeferredConsumer(object):
    def __init__(self, point):
        self.point = point
        self.point.connect_deferred_consumer(self)
        self.consumer_name = ''
        self.consumer_model = None

    def resolve_deferred_point(self, target_model):
        raise NotImplementedError()


class DeferredForeignKey(DeferredConsumer):
    def __init__(self, point, *args, **kwargs):
        super(DeferredForeignKey, self).__init__(point)

        self.fk_args = args
        self.fk_kwargs = kwargs

    def resolve_deferred_point(self, target_model):
        # if not self.consumer_name:
        #     raise RuntimeError('DeferredForeignKey не является значением')
        # import pprint
        # pp = pprint.PrettyPrinter(indent=4, depth=6)
        # pp.pprint(target_model)
        # foreign_key = models.ForeignKey(target_model, *self.fk_args, **self.fk_kwargs)
        # self.consumer_model.add_to_class(self.consumer_name, foreign_key)
        pass


class DeferredMetaclass(models.base.ModelBase):
    ''' Строчка для подготовки магии отложенных ключей '''
    def __init__(meta, cls, bases, attribs):
        super(DeferredMetaclass, meta).__init__(cls, bases, attribs)

        if not meta._meta.abstract:
            # Подготовка аттрибутов
            for name, value in attribs.items():
                if isinstance(value, DeferredConsumer):
                    value.consumer_model = cls
                    value.consumer_name = name

            # Расширение отложенной точки до оригинального класса
            point = getattr(meta, 'point', None)
            if point:
                point.resolve_deferred_point(meta)

    @classmethod
    def for_consumer(self, *bases):
        class ConsumerDeferredMetaclass(DeferredMetaclass):
            pass
        ConsumerDeferredMetaclass.__bases__ += tuple(bases)
        return ConsumerDeferredMetaclass

    @classmethod
    def for_point(self, point, *bases):
        class PointDeferredMetaclass(DeferredMetaclass):
            pass
        PointDeferredMetaclass.point = point
        PointDeferredMetaclass.__bases__ += tuple(bases)
        return PointDeferredMetaclass


# def deferred_point(point):
#     def create_deferred(target_model):
#         #point.resolve_deferred_point(target_model)
#         import pprint
#         pp = pprint.PrettyPrinter(indent=4, depth=6)
#         pp.pprint(target_model.__name__)
#         return target_model
#     return create_deferred
