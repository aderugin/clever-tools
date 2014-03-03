# -*- coding: utf-8 -*-
from clever.catalog.attributes import PseudoAttribute
from clever.catalog.attributes import AttributeManager
from clever.catalog.models import Brand
from clever.catalog.models import SectionBrand
import sys
from clever.catalog.controls import CheckboxControl
from clever.catalog import settings


# ------------------------------------------------------------------------------
@AttributeManager.register_attribute(tag='brand', verbose_name=u'Производитель', allowed_only=True)
class BrandAttribute(PseudoAttribute):
    ''' Псевдо аттрибут для брэнда '''
    title = u'Производитель'
    control_object = CheckboxControl('brand-checkbox', u'Производитель', template_name=settings.CLEVER_FILTER_BRAND_TEMPLATE)
    query_name = 'brand'

    def get_values(self, section):
        brand_fields = settings.CLEVER_BRAND_FIELDS
        brands = Brand.objects.filter(active=True, products__section=section, products__active=True).distinct().values_list('id', 'title', *brand_fields)
        params = dict(SectionBrand.objects.filter(section=section).values_list('brand', 'order'))
        def brand_order(brand):
            brand_id = brand[0]
            brand_title = brand[1]
            if brand_id in params:
                return params[brand_id]
            return sys.maxint
        return sorted(brands, key=brand_order)
