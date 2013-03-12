# -*- coding: utf-8 -*-
from clever import magic

class CatalogMetadata:
    """
    Класс для получения информации о каталоге

    Аттрибуты:
        product_model - Класс для работы с продуктами каталога
        section_model - Класс для работы с разделами каталога
        brand_model - Класс для работы с брэндами каталога
        attribute_model - ???
        product_attribute_model - ???
        section_attribute_model - ???
        section_brand_model - ???
    """

    product_model = None
    section_model = None
    brand_model = None
    attribute_model = None
    product_attribute_model = None
    section_attribute_model = None
    section_brand_model = None

    def __init__(self, product_model):
        self.product_model = product_model

        # Получение базовых моделей для каталога
        for field in magic.get_model_fields(product_model):
            if field.name == 'section':
                self.section_model = field.related.parent_model
            elif field.name == 'brand':
                self.brand_model = field.related.parent_model

        # Получение информации об модели для аттрибутов продуктов
        for field in magic.get_related_objects(product_model):
            if field.get_accessor_name() == 'attributes':
                self.product_attribute_model = field.model

        # Получение информации об модели для аттрибутов
        for field in magic.get_model_fields(self.product_attribute_model):
            if field.name == 'attribute':
                self.attribute_model = field.related.parent_model

        # Получение информации об модели
        for field in magic.get_related_objects(self.section_model):
            if field.get_accessor_name() == 'attributes_params':
                self.section_attribute_model = field.model
            elif field.get_accessor_name() == 'brand_params':
                self.section_brand_model = field.model

    @classmethod
    def from_section_model(cls, section_model):
        # Получение информации об модели
        for field in magic.get_related_objects(section_model):
            if field.get_accessor_name() == 'products':
                return cls(field.model)
        raise RuntimeError("В модели раздела %s не найдена обратная ссылка на модель продуктов" % section_model.__name__)
