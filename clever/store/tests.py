# -*- coding: utf-8 -*-
import unittest
#from .signals import order_submited
from django_any import any_model
from django.db.models import get_model
from django.db import models
from cart import Cart, Item
import clever.catalog.models as base

class Section(base.SectionBase):
    pass

class Brand(base.BrandBase):
    pass

class Product(base.ProductBase):
    class Meta:
        section_model = Section
        brand_model = Brand

class OrderTestCase(unittest.TestCase):
    def test_add_item_to_cart(self):
        self.assertEqual(1, 2)
