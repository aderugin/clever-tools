# -*- coding: utf-8 -*-
import unittest
from decimal import Decimal
from django_any import any_model
from django.db import models
from clever.catalog import models as base
from clever.store.cart import CartBase, ItemBase


# ------------------------------------------------------------------------------
class Section(base.SectionBase):
    pass


# ------------------------------------------------------------------------------
class Brand(base.BrandBase):
    pass


# ------------------------------------------------------------------------------
class Product(base.ProductBase):
    pass


# ------------------------------------------------------------------------------
class Item(ItemBase):
    pass


# ------------------------------------------------------------------------------
class Cart(CartBase):
    item_model = Item


# ------------------------------------------------------------------------------
class OrderTestCase(unittest.TestCase):

    def setUp(self):
        self.section = any_model(Section, image=None)
        self.brand = any_model(Brand, image=None)
        self.product = any_model(Product, section=self.section, brand=self.brand, image=None)

    def add_products_to_cart(self, cart, count=5):
        for i in xrange(count):
            section = any_model(Section, image=None)
            brand = any_model(Brand, image=None)
            product = any_model(Product, section=section, brand=brand, image=None)

            cart.add_product(product)

    def test_add_product_to_cart(self):
        '''Добавление нового товара'''
        cart = Cart()
        cart.add_product(self.product, 2)

        self.assertEqual(1, len(cart.items))
        self.assertEqual(2, cart.items[0].quantity)
        self.assertIsInstance(cart.items[0], Item)

    def test_add_product_twice_to_cart(self):
        '''Добавление существующего товара увеличивает кол-во штук для уже существующего товара'''
        cart = Cart()
        cart.add_product(self.product, 1)
        cart.add_product(self.product, 1)

        self.assertEqual(2, cart.items[0].quantity)

    def test_remove_product_from_cart(self):
        '''Удаление товара из корзины'''
        section = any_model(Section, image=None)
        brand = any_model(Brand, image=None)
        product = any_model(Product, section=section, brand=brand, image=None)

        cart = Cart()
        cart.add_product(self.product, 1)
        cart.add_product(product, 1)
        cart.remove_product(self.product)

        self.assertEqual(1, len(cart.items))
        self.assertNotEqual(cart.items[0].product, self.product)

    def test_clear(self):
        '''Очистка корзины'''
        cart = Cart()

        cart.add_product(self.product, 1)
        cart.clear()

        self.assertEqual(0, len(cart.items))

    def test_update_quanity_of_product_in_cart(self):
        '''Обновление кол-ва товара в корзине'''
        cart = Cart()

        cart.add_product(self.product, 1)
        cart.update_item_quantity(self.product, 3)

        self.assertEqual(3, cart.items[0].quantity)

    def test_cart_iterable(self):
        '''Перебор корзины в цикле for'''
        cart = Cart()

        self.add_products_to_cart(cart)

        copy_products = list()
        for item in cart:
            copy_products.append(item)

        self.assertEqual(len(copy_products), len(cart.items))
        self.assertEqual(cart.items, copy_products)

    def test_get_total_price(self):
        '''Получение полной стоимости для заказа [св-во Cart.total_price]'''
        cart = Cart()

        for i in xrange(5):
            section = any_model(Section, image=None)
            brand = any_model(Brand, image=None)
            product = any_model(Product, section=section, brand=brand, price=i, image=None)
            cart.add_product(product, 1)

        self.assertIsInstance(cart.total_price, Decimal)
        self.assertEqual(Decimal(10), cart.get_total_price())

    def test_product_price(self):
        '''Получение стоимости для отдельного товара'''
        cart = Cart()
        product = any_model(Product, section=self.section, brand=self.brand, price=100, image=None)
        cart.add_product(product, 2)

        self.assertIsInstance(cart.items[0].price, Decimal)
        self.assertEqual(Decimal(100), cart.items[0].price)

    def test_product_total_price(self):
        '''Получение стоимости для отдельного товара с учетом количества'''
        cart = Cart()
        product = any_model(Product, section=self.section, brand=self.brand, price=100, image=None)
        cart.add_product(product, 3)

        self.assertIsInstance(cart.items[0].price, Decimal)
        self.assertEqual(Decimal(300), cart.items[0].total_price)

    def test_empty_cart(self):
        '''Пустая корзина: is_empty == True'''
        cart = Cart()

        self.assertTrue(cart.is_empty)

        cart.add_product(self.product, 1)
        cart.remove_product(self.product)

        self.assertTrue(cart.is_empty)

    def test_no_empty_cart(self):
        '''Не пустая корзина: is_empty == False'''
        cart = Cart()

        cart.add_product(self.product, 1)
        self.assertFalse(cart.is_empty)

    def test_find_existed_product(self):
        '''Поиск товара добавленного в корзину'''
        cart = Cart()

        self.add_products_to_cart(cart)
        cart.add_product(self.product, 10)

        item = cart.find_product(self.product)
        self.assertIsInstance(item, Item)
        self.assertEqual(10, item.quantity)

    def test_find_non_existed_product(self):
        '''Поиск товара не добавленного в корзину'''
        cart = Cart()

        self.add_products_to_cart(cart)

        item = cart.find_product(self.product)
        self.assertIsNone(item)

    def test_items_count(self):
        ''' Вычисление количества продуктов в корзине'''
        cart = Cart()
        self.add_products_to_cart(cart, 6)

        self.assertEqual(6, len(cart))
