# -*- coding: utf-8 -*-
import functools
from djcelery_transactions import task
from celery.decorators import periodic_task
from celery.schedules import crontab
from clever.catalog.models import Brand
from clever.catalog.models import Section
from clever.catalog.models import Attribute
from clever.catalog.models import ProductAttribute
from .forms import FilterForm


def load_all_models(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Load all deffered models
        from django.db import models
        models.get_models(include_auto_created=True)
        func(*args, **kwargs)
    return wrapper


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
@load_all_models
def invalidate_section(section_id):
    try:
        section = Section.objects.get(id=section_id)
        do_invalidate_section(section)
    except Section.DoesNotExist:
        pass


@task(ignore_result=True)
@load_all_models
def invalidate_brand(brand_id):
    try:
        brand = Brand.objects.get(id=brand_id)
        for section in brand.descendant_sections:
            do_invalidate_section(section)
    except Brand.DoesNotExist:
        pass


@task(ignore_result=True)
@load_all_models
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
@load_all_models
def invalidate_catalog():
    do_invalidate_catalog()
