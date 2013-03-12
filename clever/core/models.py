# -*- coding: utf-8 -*-
"""
:mod:`clever.core.models` -- Ядро для работы с моделями
===================================

.. moduleauthor:: Семен Пупков (semen.pupkov@gmail.com)
"""
from django.db import models
from django.db.models import query
from hashlib import md5
from time import time
from model_utils import managers
from model_utils import fields
from caching import base as cache_machine
from clever import magic
import autoslug
import os


def generate_upload_name(instance, filename, prefix=None, unique=False):
    """
    Авто генерация имени для файлов и изображений, загруженных с помощью  FileField и ImageField.

    .. sectionauthor:: Семен Пупков (semen.pupkov@gmail.com)
    """
    if instance == None:
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
