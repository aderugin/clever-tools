# -*- coding: utf-8 -*-


def create_cache_identifiers(func, section):
    if section:
        cache_id = 'filter.section.%s.%d' % (func.__name__, section.id)
        cache_tag = 'section.%d' % section.id
    else:
        cache_id = 'filter.section.%s.%s' % (func.__name__, 'all')
        cache_tag = 'section.%s' % 'all'
    return cache_id, cache_tag