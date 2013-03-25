# -*- coding: utf-8 -*-
"""
:mod:`clever.catalog.view` -- Виды для базовой корзины
========================================================

В данном модуле хранится базовый набор видов для работы с корзиной и заказами.

"""

from __future__ import absolute_import
from django.views.generic import TemplateView

# template_name = "about.html"


# Контроллер для просмотра элементов в корзине
class CartIndexView(DetailView):
    pass

# Контроллер для очистки элементов в корзине
class CartClearView(DetailView):
    pass

# Контроллер для добавление продукта в корзину
class CartAddProductView(DetailView):
    pass

# Удаление продукта из корзины
class CartRemoveProductView(DetailView):
    pass

# Обновление кол-ва единиц продукта в корзине
class CartUpdateProductView(DetailView):
    redirect_to = 'cart_index'
