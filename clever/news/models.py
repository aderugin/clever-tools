# -*- coding: utf-8 -*-

from clever.deferred import DeferredPoint

# ------------------------------------------------------------------------------
Section = DeferredPoint('Section')

# ------------------------------------------------------------------------------
News = DeferredPoint('News')


from django.db import models
from clever.deferred.models import DeferredModelMetaclass
from clever.deferred.fields import DeferredForeignKey
from caching import base as cache_machine
from clever.core.models import SitePageMixin
from clever.core.models import extend_meta
from datetime import date


# ------------------------------------------------------------------------------
class SectionBase(cache_machine.CachingMixin, SitePageMixin):
    ''' Раздел новостей '''
    class Meta:
        abstract = True

    __metaclass__ = DeferredModelMetaclass.for_point(
        Section,
        extend_meta(
            verbose_name=u'Раздел новостей',
            verbose_name_plural=u'Разделы новостей'
        )
    )

    @models.permalink
    def get_absolute_url(self):
        return ('news_section', (), {'slug': self.slug})


# ------------------------------------------------------------------------------
class NewsBase(cache_machine.CachingMixin, SitePageMixin):
    ''' Новость '''
    class Meta:
        abstract = True

    __metaclass__ = DeferredModelMetaclass.for_point(
        Section,
        extend_meta(
            verbose_name=u'Новость',
            verbose_name_plural=u'Новости',
            ordering=['-publish_at']
        )
    )

    section = DeferredForeignKey(Section, verbose_name=u'Раздел', null=False, blank=False)
    publish_at = models.DateField(verbose_name=u'Дата публикации', default=date.today)

    @models.permalink
    def get_absolute_url(self):
        return ('news_detail', (), {'slug': self.slug})
