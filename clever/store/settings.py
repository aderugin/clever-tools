#*- coding: utf-8 -*-
"""
:mod:`clever.store.settings` -- Модуль для получение настроек корзины
=====================================================================================

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
.. moduleauthor:: Антон Вахмин <html.ru@gmail.com>
"""
from django.conf import settings

# Настройка класса для базового класса корзины
CLEVER_CART_CLASS = getattr(settings, 'CLEVER_CART_CLASS', 'clever.store.cart.CartBase')

# Настройка класса для базового класса элемента корзины
CLEVER_CART_ITEM_CLASS = getattr(settings, 'CLEVER_ITEM_CLASS', 'clever.store.cart.ItemBase')

# Настройка имени переменной в сессии для хранения корзины
CLEVER_CART_SESSION_NAME = getattr(settings, 'CART_SESSION_NAME', 'clever-cart')
