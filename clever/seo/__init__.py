# -*- coding: utf-8 -*-
from rollyourown import seo
from .settings import CLEVER_SEO_CLASS
from clever.magic import load_class
from django.db.models.signals import pre_save
from django.db.models.fields import FieldDoesNotExist

def remove_unused_metadata(instance, *args, **kwargs):
    '''
    Удаление старых метаданных из SEO
    '''
    clazz = instance.__class__

    try:
        field = clazz._meta.get_field('_path')

        qs = clazz.objects.filter(_path=instance._path)
        if instance.pk:
            qs = qs.exclude(id=instance.pk)
        for old_inst in qs:
            old_inst.delete()

    except FieldDoesNotExist:
        pass


SeoClass = load_class(CLEVER_SEO_CLASS)
for clazz in SeoClass._meta.models.values():
    pre_save.connect(remove_unused_metadata, sender=clazz, weak=False)
