# -*- coding: utf-8 -*-

from django.db import models
from caching import base as cache_machine
from clever.core.models import TimestableMixin
from clever.core.models import ActivableMixin
from clever.core.models import generate_upload_name
import autoslug


class Slider(cache_machine.CachingMixin, TimestableMixin, ActivableMixin):
    class Meta:
        verbose_name=u'Слайдер'
        verbose_name_plural=u'Слайдеры'

    title = models.CharField(verbose_name=u"Название", max_length=255)
    slug = autoslug.AutoSlugField(verbose_name=u"ЧПУ сегмент", populate_from='title', sep='-', unique=True)

    def __unicode__(self):
        return self.title


class Item(cache_machine.CachingMixin, TimestableMixin, ActivableMixin):
    class Meta:
        verbose_name=u'Элемент слайдера'
        verbose_name_plural=u'Элементы слайдера'
        ordering = ('sort',)

    slider = models.ForeignKey(Slider, verbose_name=u'Слайдер', related_name='items')
    title = models.CharField(verbose_name=u"Название", max_length=255, blank=True, null=True)
    url = models.URLField(verbose_name=u'URL', blank=True, null=True)
    image = models.ImageField(upload_to=generate_upload_name, verbose_name=u'Изображение')
    sort = models.PositiveIntegerField(verbose_name=u'Индекс сортировки', default=500, blank=True)

    def __unicode__(self):
        return self.title
