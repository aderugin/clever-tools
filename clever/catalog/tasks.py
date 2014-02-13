# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from cache_tagging.django_cache_tagging import get_cache
from djcelery_transactions import task
from .models import Section
import requests
import urlparse


@task(ignore_result=True)
def invalidate_section(section_id):
    try:
        section = Section.objects.get(id=section_id)
        current_site = Site.objects.get_current()
        cache_tag = 'section.%d' % section.id
        cache = get_cache('catalog')
        cache.invalidate_tags(cache_tag)

        # Create cache for page
        url = urlparse.urljoin('http://%s' % current_site.domain, section.get_absolute_url())
        requests.get(url)
    except Section.DoesNotExist:
        pass


@task(ignore_result=True)
def invalidate_catalog():
    for section in Section.objects.all():
        invalidate_section(section.id)
