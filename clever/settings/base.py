# -*- coding: utf-8 -*-
from clever.settings.settings import CLEVER_SETTINGS_TIMEOUT
from django.core.cache import get_cache
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.base import Model
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from caching import base as cache_machine


_models = {}
_options = {}


def get_fields(model):
    """
    _meta - не документирована, так что это мой костыль для защиты
    """
    return model._meta.fields


def get_models():
    return _models


class SettingsMetaclass(ModelBase):
    def __new__(cls, name, bases, attrs):
        model = super(SettingsMetaclass, cls).__new__(cls, name, bases, attrs)

        if model.__module__ != __name__:
            _models[model.__module__ + "." + name] = model
            fields = get_fields(model)
            for field in fields:
                if not field.name in ['id', '_site']:
                    if field.name in _options:
                        raise RuntimeError("Option %s.%s already exists" % (model.__name__, field.name))
                    else:
                        _options[field.name] = model
        return model


class SettingsModel(cache_machine.CachingMixin, Model):
    class Meta:
        abstract = True
    __metaclass__ = SettingsMetaclass
    _site = models.ForeignKey(Site, unique=True, blank=True, editable=False)

    def clean(self):
        if self._site is None:
            self._site = Site.objects.get_current()


def get_option(name, default=None):
    cache = get_cache('catalog')
    cache_id = 'clever.settings:%s' % name
    value = cache.get(cache_id)
    if value:
        model = _options.get(name, None)
        if model is not None:
            try:
                site = Site.objects.get_current()
                object = model.objects.filter(_site=site)[0]
                value = getattr(object, name, default)
                cache.set(cache_id, value, timeout=CLEVER_SETTINGS_TIMEOUT)
                return value
            except IndexError:
                pass
            except ObjectDoesNotExist:
                pass
        return default
    return value
