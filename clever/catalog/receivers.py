# -*- coding: utf-8 -*-
"""
:mod:`clever.catalog.receivers` -- Обработчики событий базового каталога
========================================================================

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
"""

from .models import SectionBase as Section
from .models import BrandBase as Brand
from .models import ProductBase as Product
from .models import ProductAttributeBase as ProductAttribute
from .models import SectionAttributeBase as SectionAttribute

from .tasks import invalidate_section

from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver


@receiver(post_save, weak=False)
@receiver(pre_delete, weak=False)
def handle_section_invalidate(sender, instance, **kwargs):
    if issubclass(sender, Section):
        invalidate_section.delay(instance.id)

    elif issubclass(sender, Product):
        invalidate_section.delay(instance.section.id)

    elif issubclass(sender, ProductAttribute):
        invalidate_section.delay(instance.product.section.id)

    elif issubclass(sender, SectionAttribute):
        invalidate_section.delay(instance.section.id)

    elif issubclass(sender, Brand):
        sections = instance.descendant_sections.values_list('id', flat=True)
        for section_id in sections:
            invalidate_section.delay(section_id)
