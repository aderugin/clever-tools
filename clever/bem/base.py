# -*- coding: utf-8 -*-

from django.utils.importlib import import_module
# from django.utils.module_loading import module_has_submodule
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


# ------------------------------------------------------------------------------
class BemTag(object):
    def get_bemjson_context(self, request, context):
        ''' Создание блока для бэма '''
        raise NotImplementedError()


# ------------------------------------------------------------------------------
class BemManager(object):
    def load_app(self, app_name, app_tag):
        """
        Loads the app with the provided fully qualified name, and returns the
        model module.
        """
        # app_module = import_module(app_name)
        try:
            models = import_module('.bemtags.' + app_tag, app_name)
        except ImportError:
            return None
        return models

    def get_app(self, app_label, app_tag, emptyOK=False):
        """
        Returns the module containing the models for the given app_label. If
        the app has no models in it and 'emptyOK' is True, returns None.
        """

        for app_name in settings.INSTALLED_APPS:
            if app_label == app_name.split('.')[-1]:
                mod = self.load_app(app_name, app_tag)
                if mod is None:
                    if emptyOK:
                        return None
                    raise ImproperlyConfigured("App with label %s is missing a bemtags.%s.py module." % (app_label, app_tag))
                else:
                    return mod
        raise ImproperlyConfigured("App with label %s could not be found" % app_label)
