# -*- coding: utf-8 -*-
from clever.catalog.attributes import PseudoAttribute
from clever.catalog.attributes import AttributeManager
from clever.catalog.models import Brand


# ------------------------------------------------------------------------------
@AttributeManager.register_attribute(tag='brand', verbose_name=u'Производитель')
class BrandAttribute(PseudoAttribute):
    ''' Псевдо аттрибут для брэнда '''

    control_object = AttributeManager.get_control('checkbox')
    query_name = 'brand'

    def get_values(self, section):
        return Brand.brands.filter(products__section=section).distinct().values_list('id', 'title')
