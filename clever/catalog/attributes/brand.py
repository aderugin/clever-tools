# -*- coding: utf-8 -*-

class BrandAttribute(AbstractAttribute):
    ''' Псевдо аттрибут для брэнда '''

    title = 'Производитель'
    control_object = CheckboxControl()
    query_name = 'brand'
    uid = 'brand'

    def get_values(self, section):
        metadata = CatalogMetadata.from_section_model(section)
        return metadata.brand_model.brands.filter(products__section=section).distinct().values_list('id', 'title')
