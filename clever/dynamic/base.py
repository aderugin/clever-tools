# -*- coding: utf-8 -*-
import contextlib
import copy
import threading
from . import settings


class DynamicSettings(object):
    """ Хранит настройки для отдельного запроса Django или задачи Celery """
    def __init__(self):
        config = getattr(settings, 'CLEVER_DYNAMIC_SETTINGS', {})
        for name, value in config.items():
            setattr(self, name, value)

    def clone(self):
        return copy.copy(self)

    @staticmethod
    def reload_settings():
        thread_local = threading.local()
        setattr(thread_local, 'dynamic_settings', DynamicSettings())

    @staticmethod
    def get():
        thread_local = threading.local()
        return getattr(thread_local, 'dynamic_settings', DynamicSettings())

    @staticmethod
    def set(conf):
        thread_local = threading.local()
        return getattr(thread_local, 'dynamic_settings', conf)


@contextlib.contextmanager
def update_dynamic_settings(**kwargs):
    # store old settings
    old_settings = DynamicSettings.get()

    # copy old settings to new and update
    new_settings = old_settings.clone()
    for key, value in kwargs.items():
        setattr(new_settings, key, value)
    DynamicSettings.set(new_settings)

    # run context
    yield

    # restore old settings
    DynamicSettings.set(old_settings)
