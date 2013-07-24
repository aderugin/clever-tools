# -*- coding: utf-8 -*-
from clever.catalog.attributes import PseudoAttribute
from clever.catalog.attributes import AttributeManager
from clever.catalog.models import Brand
from clever.catalog.models import SectionBrand
import sys


# ------------------------------------------------------------------------------
@AttributeManager.register_attribute(tag='brand', verbose_name=u'Производитель', allowed_only=True)
class BrandAttribute(PseudoAttribute):
    ''' Псевдо аттрибут для брэнда '''

    control_object = AttributeManager.get_control('checkbox')
    query_name = 'brand'

    def get_values(self, section):
        brands = Brand.objects.filter(active=True, products__section=section, products__active=True).distinct().values_list('id', 'title')
        params = dict(SectionBrand.objects.filter(section=section).values_list('brand', 'order'))
        def brand_order(brand):
            brand_id, brand_title = brand
            if brand_id in params:
                return params[brand_id]
            return sys.maxint
        return sorted(brands, key=brand_order)
