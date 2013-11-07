# # -*- coding: utf-8 -*-
# #author: Semen Pupkov (semen.pupkov@gmail.com)

# from django.utils import unittest
# from django_any import any_model
# from clever.catalog.models import SectionModel


# class SectionNestingTest(unittest.TestCase):
#     def test_catalog_unlimited_nesting_save(self):
#         parent = any_model(UnlimitedLevelSection, image=None, parent=None)
#         for i in xrange(1, 100):
#             child = any_model(UnlimitedLevelSection, image=None, parent=parent)
#             self.assertEqual(parent, child.parent)
#             parent = child


# class UnlimitedLevelSection(SectionModel):
#     class Meta:
#         nesting_level = None
