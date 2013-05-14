# -*- coding: utf-8 -*-
from mptt.models import MPTTModel, TreeForeignKey
from django.db import models
from django.conf import settings

HOMEPAGE_SLUG = 'homepage'


class Page(MPTTModel):
    class Meta:
        verbose_name = u'Статичная страница'
        verbose_name_plural = u'Статичные страницы'
        ordering = ['tree_id', 'lft']

    page_templates = (
        ('default', u'Стандартная страница'),
    )

    if hasattr(settings, 'PAGE_TEMPLATES'):
        page_templates += settings.PAGE_TEMPLATES

    parent = TreeForeignKey('self', blank=True, null=True,
                            related_name='children', verbose_name=u'Родительская страница',
                            help_text=u'Все страницы должны быть привязаны к главной. На нулевом уровне может находится только одна страница')
    active = models.BooleanField(default=True, verbose_name=u'Активность')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name=u'Дата обновления')

    title = models.CharField(max_length=300, verbose_name=u'Название')
    slug = models.SlugField(max_length=200, unique=True, help_text=u'Для главной страницы значение должно быть `%s`' % HOMEPAGE_SLUG)
    path = models.CharField(max_length=300, verbose_name=u'Полный путь', null=True, blank=True, help_text=u'Строится автоматически')
    template = models.CharField(max_length=50, verbose_name=u'Шаблон', null=True, blank=True)
    text = models.TextField(blank=True, verbose_name=u'Текст')

    def __unicode__(self):
        return self.title

    def generate_path(self):
        '''
        Строит полный путь включая всех родителей
        '''
        if self.slug != HOMEPAGE_SLUG:
            ontology = []
            if self.parent:
                for item in self.parent.get_ancestors():
                    if item.level != 0:
                        ontology.append(item.slug)
                if self.parent.level != 0:
                    ontology.append(self.parent.slug)
            ontology.append(self.slug)
            return '/' + '/'.join(ontology) + '/'
        else:
            return '/'

    def save(self):
        self.path = self.generate_path()
        super(Page, self).save()

    def get_absolute_url(self):
        return self.path
