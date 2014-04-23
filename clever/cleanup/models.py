import os
import logging
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.db.models.loading import cache
from django.core.files.storage import get_storage_class
from sorl.thumbnail import default

logger = logging.getLogger(__name__)


def find_models_with_imagefield():
    result = set()
    for app in cache.get_apps():
        model_list = cache.get_models(app)
        for model in model_list:
            for field in model._meta.fields:
                if isinstance(field, models.ImageField):
                    result.add(model)
                    break
    return [model for model in result]


def remove_old_files(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = instance.__class__.objects.get(pk=instance.pk)
    except instance.DoesNotExist:
        return

    for field in instance._meta.fields:
        if not isinstance(field, models.ImageField):
            continue
        old_file = getattr(old_instance, field.name)
        new_file = getattr(instance, field.name)
        storage = old_file.storage
        if old_file and old_file != new_file:
            try:
                default.backend.delete(old_file)
            except Exception as e:
                logger.exception("Unexpected exception while attempting to delete old file '%s'" % old_file.name)


def remove_files(sender, instance, **kwargs):

    for field in instance._meta.fields:
        if not isinstance(field, models.ImageField):
            continue
        file_to_delete = getattr(instance, field.name)
        storage = file_to_delete.storage
        if file_to_delete:
            try:
                default.backend.delete(file_to_delete)
            except Exception as e:
                logger.exception("Unexpected exception while attempting to delete file '%s'" % file_to_delete.name)


for model in find_models_with_imagefield():
    pre_save.connect(remove_old_files, sender=model, weak=False)
    post_delete.connect(remove_files, sender=model, weak=False)
