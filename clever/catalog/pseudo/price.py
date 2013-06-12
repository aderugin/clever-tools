# -*- coding: utf-8 -*-
from clever.catalog.attributes import PseudoAttribute
from clever.catalog.attributes import AttributeManager
from clever.catalog.models import Product
from django.db import models
from clever.catalog.controls import RangeControl
from clever.catalog.types import PriceType


# ------------------------------------------------------------------------------
@AttributeManager.register_attribute(tag='price', verbose_name=u'Цена', allowed_only=True)
class PriceAttribute(PseudoAttribute):
    ''' Псевдо аттрибут для брэнда '''
    title = 'Производитель'
    control_object = RangeControl('range-price', u'Диапазон цен', template_name='blocks/input/price_range.html')
    type_object = PriceType('price', u'Цена')
    query_name = 'price'

    def get_values(self, section):
        # return Brand.brands.filter(products__section=section).distinct().values_list('id', 'title')
        prices = Product.objects.filter(section=section).aggregate(max_price=models.Max('price'), min_price=models.Min('price'))
        return (
            (prices['min_price'], prices['min_price']),
            (prices['max_price'], prices['max_price']),
        )
