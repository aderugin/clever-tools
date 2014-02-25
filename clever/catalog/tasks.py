# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from cache_tagging.django_cache_tagging import get_cache
from djcelery_transactions import task
from celery.decorators import periodic_task
from .settings import CLEVER_FILTER_TIMEOUT
from .models import Section
from .models import PseudoSection
import requests
import urlparse
import datetime


@task(ignore_result=True)
def invalidate_section(section_id):
    log = invalidate_section.get_logger()
    current_site = Site.objects.get_current()

    try:
        section = Section.objects.get(id=section_id)

        log.info('Invalidate cache for section "%s" [%d]', section.title, section.id)
        cache_tag = 'section.%d' % section.id
        cache = get_cache('catalog')
        cache.invalidate_tags(cache_tag)

        # Create cache for page
        log.info('Recreate cache for section "%s" [%d]', section.title, section.id)
        url = urlparse.urljoin('http://%s' % current_site.domain, section.get_absolute_url())
        requests.get(url)

        if PseudoSection.deferred_instance:
            pseudo_sections = PseudoSection.objects.filter(section_id=section.id)
            for pseudo_section in pseudo_sections:
                log.info('Recreate cache for pseudo section "%s - %s" [%d]', section.title, pseudo_section.title, section.id)
                url = urlparse.urljoin('http://%s' % current_site.domain, pseudo_section.get_absolute_url())
                requests.get(url)


    except Section.DoesNotExist:
        pass


@task(ignore_result=True)
def invalidate_catalog():
    log = invalidate_catalog.get_logger()
    log.info('Start invalidate cache for all sections')
    for section in Section.objects.all():
        invalidate_section(section.id)
    log.info('FInish invalidate cache for all sections')


@periodic_task(run_every=datetime.timedelta(seconds=CLEVER_FILTER_TIMEOUT))
def periodic_invalidate_catalog():
    invalidate_catalog()
