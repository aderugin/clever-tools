# -*- coding: utf-8 -*-
from clever.catalog.attributes import PseudoAttribute
from clever.catalog.attributes import AttributeManager
from clever.catalog.models import Product
from django.db import models
from clever.catalog.controls import RangeControl
from clever.catalog.types import PriceType
from clever.catalog import settings
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR


# ------------------------------------------------------------------------------
@AttributeManager.register_attribute(tag='price', verbose_name=u'Цена', allowed_only=True)
class PriceAttribute(PseudoAttribute):
    ''' Псевдо аттрибут для брэнда '''
    title = u'Цена'
    control_object = RangeControl(
        'range-price', u'Диапазон цен',
        template_name=settings.CLEVER_FILTER_PRICE_TEMPLATE,
        max_args=settings.CLEVER_FILTER_PRICE_MAX_ARGS,
        min_args=settings.CLEVER_FILTER_PRICE_MIN_ARGS
    )
    type_object = PriceType('price', u'Цена')
    query_name = 'price'

    def get_values(self, sections):
        prices = Product.objects.filter(section__in=sections, active=True).aggregate(max_price=models.Max('price'), min_price=models.Min('price'))

        if isinstance(prices['min_price'], Decimal):
            prices['min_price'] = prices['min_price'].to_integral_exact(ROUND_FLOOR)
            prices['max_price'] = prices['max_price'].to_integral_exact(ROUND_CEILING)
        return (
            (prices['min_price'], prices['min_price']),
            (prices['max_price'], prices['max_price']),
        )
