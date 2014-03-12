# -*- coding: utf-8 -*-
from django.conf import settings


class CartMiddleware(object):
    '''
    Данный класс добавляет в request информацию о пользовательской корзине
    '''

    def process_request(self, request):
        request.cart = self.load_cart(request)
        # request.breadcrumbs = Breadcrumbs()
        # request.breadcrumbs._clean()
