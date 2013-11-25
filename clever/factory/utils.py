# -*- coding: utf-8 -*-

import os
import random
import json
import factory
from django.db.models import Model
from django.core.files import File
from factory import django
import decimal

# import codecs
# with codecs.open('./streets.txt', encoding='utf-8') as f:
#     STREETS = f.read().splitlines()
#     STREETS = filter(lambda street: bool(street), map(lambda street: street.strip(), STREETS))

IMAGES_PATH = os.path.join(os.path.dirname(__file__), 'images/custom')
IMAGES = [
    os.path.join(path, filename)
    for path, dirs, files in os.walk(IMAGES_PATH)
    for filename in files
    if not filename.endswith(".bak")
]

BRANDS_PATH = os.path.join(os.path.dirname(__file__), 'fixtures/brands.json')
BRANDS_IMAGES = os.path.join(os.path.dirname(__file__), 'images/brands')
with open(BRANDS_PATH) as f:
    BRANDS_DATA = json.loads(f.read())

def random_model_instance(model, queryset_callback=None):
    def wrapper(item):
        queryset = model.objects.all()
        if queryset_callback:
            queryset = queryset_callback(queryset)
        count = queryset.count()
        i = random.randint(0, count - 1)
        return queryset.all()[i]
    return wrapper


def load_image(path, file):
    return File(open(os.path.join(path, file)))


def random_element_and_remove(array):
    item = random.choice(array)
    index = array.index(item)
    del array[index]
    return item


def random_image(instance):
    return File(open(random.choice(IMAGES), 'r'))


def random_price(instance):
    return decimal.Decimal(random.randint(100, 10000) * 100) / 100


def random_attribute_type(instance):
    from clever.catalog import settings
    return random.choice(settings.CLEVER_ATTRIBUTES_TYPES)

def random_attribute_control(instance):
    from clever.catalog import settings
    control = None
    while not control or (control == u'range' and not instance.type_object.is_range):
        control = random.choice(settings.CLEVER_ATTRIBUTES_TYPES)
    return control

def ranfom_attribute_value(instance):
    attribute = instance.attribute
    if attribute.type == u'integer':
        return random.randint(0, 1000)
    elif attribute.type == u'float':
        return random.random() * random.randint(0, 1000)
    elif attribute.type == u'price':
        return attribute.price
    elif attribute.type == u'string':
        return u'Random'
    return None

class BrandFactory(django.DjangoModelFactory):
    ''' Генератор для производителя '''
    title = factory.Sequence(lambda n: 'Brand {0}'.format(n))
    text = factory.Sequence(lambda n: 'Text {0}'.format(n))

    @factory.post_generation
    def generate_standart(self, create, extracted, **kwargs):
        brand = random_element_and_remove(BRANDS_DATA)

        self.title = brand['title']
        self.text = brand['text']
        self.image = load_image(BRANDS_IMAGES, brand['image'])


class SectionFactory(django.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Section {0}'.format(n))
    text = factory.Sequence(lambda n: 'Text {0}'.format(n))
    image = factory.LazyAttribute(random_image)


class ProductFactory(django.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Product {0}'.format(n))
    image = factory.LazyAttribute(random_image)
    price = factory.LazyAttribute(random_price)


class AttributeFactory(django.DjangoModelFactory):
    main_title = factory.Sequence(lambda n: 'Attribute {0}'.format(n))

    type = factory.LazyAttribute(random_attribute_type)
    control = factory.LazyAttribute(random_attribute_control)



class AttributeValueFactory(django.DjangoModelFactory):
    value = factory.LazyAttribute(ranfom_attribute_value)
