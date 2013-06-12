from clever.catalog.attributes import AbstractAttribute
from clever.catalog.attributes import AttributeManager


# ------------------------------------------------------------------------------
@AttributeManager.register_attribute(tag='price', verbose_name=u'Цена')
class BrandAttribute(AbstractAttribute):
    ''' Псевдо аттрибут для брэнда '''
    title = 'Производитель'
    control_object = AttributeManager.get_control('range')
    query_name = 'brand'
    uid = 'brand'

    def get_values(self, section):
        return Brand.brands.filter(products__section=section).distinct().values_list('id', 'title')
