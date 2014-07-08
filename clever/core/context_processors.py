from cache_tagging.django_cache_tagging import get_cache
from django.conf import settings


def django_settings(context):
    # get compress version and increment it
    cache = get_cache('default')
    version = cache.get('CLEVER_COMPRESS_VERSION', 1)
    return {
        'DEBUG': settings.DEBUG,
        'TEMPLATE_DEBUG': settings.TEMPLATE_DEBUG,
        'COMPRESS_VERSION': version,
    }