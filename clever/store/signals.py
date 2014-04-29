# -*- coding: utf-8 -*-
from django.dispatch.dispatcher import Signal


add_item = Signal(providing_args=['cart', 'item'])

remove_item = Signal(providing_args=['cart', 'item'])

update_item = Signal(providing_args=['cart', 'item'])