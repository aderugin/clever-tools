# -*- coding: utf-8 -*-
from django.dispatch.dispatcher import Signal


add_item = Signal(providing_args=['cart', 'item'])

remove_item = Signal(providing_args=['cart', 'item'])

update_item = Signal(providing_args=['cart', 'item'])

pre_order_create = Signal(providing_args=['order', 'cart'])

post_order_create = Signal(providing_args=['order'])