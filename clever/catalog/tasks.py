# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from cache_tagging.django_cache_tagging import get_cache
from djcelery_transactions import task
from celery.decorators import periodic_task
from celery.schedules import crontab
from .models import Brand
from .models import Section
from .models import Attribute
from .models import ProductAttribute
from .models import PseudoSection
from .forms import FilterForm
import requests
import urlparse


def do_invalidate_section(section):
    """ Do invalidate section """
    logger = invalidate_section.get_logger()
    FilterForm.get_product_indexes.invalidate_cache(section, logger)
    FilterForm.get_pseudo_attributes.invalidate_cache(section, logger)
    FilterForm.get_attributes.invalidate_cache(section, logger)


def do_invalidate_catalog():
    """ Full invalidate of catalog """
    log = invalidate_catalog.get_logger()
    log.info('Start invalidate cache for all sections')
    for section in Section.objects.all():
        do_invalidate_section(section)
    log.info('Finish invalidate cache for all sections')


@task(ignore_result=True)
def invalidate_section(section_id):
    try:
        section = Section.objects.get(id=section_id)
        do_invalidate_section(section)
    except Section.DoesNotExist:
        pass


@task(ignore_result=True)
def invalidate_brand(brand_id):
    try:
        brand = Brand.objects.get(id=brand_id)
        for section in brand.descendant_sections:
            do_invalidate_section(section)
    except Brand.DoesNotExist:
        pass


@task(ignore_result=True)
def invalidate_attribute(attribute_id):
    try:
        attribute = Attribute.objects.get(id=attribute_id)
        products = ProductAttribute.objects.filter(attribute_id=attribute.id).values_list('product_id', flat=True).distinct()
        sections = Section.objects.filter(products__id__in=products).distinct()
        for section in sections:
            do_invalidate_section(section)
    except Attribute.DoesNotExist:
        pass


@periodic_task(run_every=crontab(hour=3, minute=0))
def invalidate_catalog():
    do_invalidate_catalog()
