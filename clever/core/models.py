# -*- coding: utf-8 -*-
"""
:mod:`clever.core.models` -- Ядро для работы с моделями
===================================

.. moduleauthor:: Семен Пупков (semen.pupkov@gmail.com)
.. moduleauthor:: Василий Шередеко (piphon@gmail.com)
"""
from django.db import models
from django.db.models import query
from django.db.models import signals
from django.core import exceptions
from hashlib import md5
from time import time
from mptt import managers as mptt_managers
from model_utils import managers
from model_utils import fields
from caching import base as cache_machine
import autoslug
import os
import uuid


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


class StringWithTitle(str):
    def __new__(cls, value, title):
        instance = str.__new__(cls, value)
        instance._title = title
        return instance

    def title(self):
        return self._title

    __copy__ = lambda self: self
    __deepcopy__ = lambda self, memodict: self


class SortableMixin(models.Model):
    """
    Миксин для сортировки
    """
    class Meta:
        abstract = True

    sort = models.PositiveIntegerField(blank=True)

    @staticmethod
    def pre_save(sender, instance, **kwargs):
        if (not instance.sort):
            last_qs = sender.objects.reverse()
            if (last_qs.count() > 0 and last_qs[0].sort):
                instance.sort = int(last_qs[0].sort) + 100
            else:
                instance.sort = 1000
        return instance


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
    slug = autoslug.AutoSlugField(verbose_name=u"ЧПУ сегмент", max_length=255, populate_from='title', sep='-', unique=True, editable=True, blank=True)

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


class SitePageMixin(TimestableMixin, ActivableMixin, TitleMixin, PageMixin):
    class Meta:
        abstract = True


class CachingPassThroughManager(managers.PassThroughManager, cache_machine.CachingManager):
    pass


class TreeCachingPassThroughManager(mptt_managers.TreeManager, CachingPassThroughManager):
    pass


def extend_meta(**kwargs):
    ''' Расширение класса Meta для Django '''
    class DefaultMeta:
        pass

    class MetaExtendMetaclass(models.base.ModelBase):
        def __new__(cls, name, bases, attribs):
            meta = attribs.get('Meta', DefaultMeta)
            for key, value in kwargs.items():
                if not hasattr(meta, key):
                    setattr(meta, key, value)
            attribs['Meta'] = meta
            return super(MetaExtendMetaclass, cls).__new__(cls, name, bases, attribs)

    return MetaExtendMetaclass


def save_default_image(image_item_attr, image_file_attr='image', item_image_attr='image', images_related_name='images'):
    def decorator(cls):
        def save_default_image_handler(instance, created, **kwargs):
            try:
                item = getattr(instance, image_item_attr)
                images = getattr(item, images_related_name).order_by('-id')
                if len(images):
                    setattr(item, item_image_attr, getattr(images[0], image_file_attr))
                    item.save()
            except exceptions.ObjectDoesNotExist:
                pass

        signals.post_save.connect(save_default_image_handler, sender=cls, weak=False)
        return cls

    return decorator
