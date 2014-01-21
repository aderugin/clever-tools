# -*- coding: utf-8 -*-

import decimal


class Cart(object):
    session_key = 'django-cart'
    price_key = 'real_price'
    product_model = None

    def __init__(self, request):
        self.request = request
        if not self.session_key in self.request.session:
            self.request.session[self.session_key] = {}

    def get_key(self, item):
        key = str(item['id'])
        return key

    def add(self, id, count=1, extra={}, increase=True):
        item = {
            'id': id,
            'count': count,
            'extra': extra
        }
        key = self.get_key(item)
        if key in self.request.session[self.session_key] and increase == True:
            self.request.session[self.session_key][key]['count'] += count
        else:
            self.request.session[self.session_key][key] = item
        self.request.session.modified = True

    def update(self, key, count=None, **kwargs):
        if count:
            self.request.session[self.session_key][key]['count'] = int(count)
            # if count < 1:
            #     self.delete(key)
        if 'extra' in kwargs:
            self.request.session[self.session_key][key]['extra'] = kwargs['extra']
            new_key = self.get_key(self.request.session[self.session_key][key])
            if key != new_key:
                self.request.session[self.session_key][new_key] = self.request.session[self.session_key][key]
                del self.request.session[self.session_key][key]
        self.request.session.modified = True

    def delete(self, key):
        del self.request.session[self.session_key][key]
        self.request.session.modified = True

    def count(self):
        return sum([x[1]['count'] for x in self.request.session[self.session_key].iteritems()])

    def prepare_data(self):
        if hasattr(self, 'product_list'):
            return None
        product_pks = list(set(map(lambda x: x[1]['id'], self.request.session[self.session_key].items())))
        self.product_list = []
        self.product_prices = {}
        if len(product_pks) > 0:
            self.product_list = self.product_model.objects.filter(pk__in=product_pks)
            self.product_prices = {str(x['id']): x[self.price_key] for x in self.product_list.values('id', self.price_key)}

    def remove_missing(self):
        product_pks = [str(x.id) for x in self.product_list]
        items_copy = self.request.session[self.session_key].copy()
        for item in items_copy.iteritems():
            if  not item[1]['id'] in product_pks:
                del self.request.session[self.session_key][item[0]]

    def get_item_price(self, item):
        return (self.product_prices[item['id']] * item['count']) if item['id'] in self.product_prices else 0

    def get_total_price(self):
        self.prepare_data()
        self.remove_missing()
        price = decimal.Decimal(0)
        for item in self.request.session[self.session_key].iteritems():
            price += self.get_item_price(item[1])
        return price

    def get_with_products(self):
        self.prepare_data()
        self.remove_missing()
        item_list = [x[1] for x in self.request.session[self.session_key].iteritems()]
        product_dict = {str(x.id): x for x in self.product_list}
        for item in item_list:
            item['key'] = self.get_key(item)
            item['product'] = product_dict[item['id']]
            item['price'] = self.get_item_price(item)
        return item_list


class CartWithOptions(Cart):
    option_model = None

    def get_key(self, item):
        key = super(CartWithOptions, self).get_key(item)
        if len(item['extra']) > 0:
            key += '_' + '_'.join(sorted(str(x) for x in item['extra'].keys()))
        return key

    def remove_missing(self):
        super(CartWithOptions, self).remove_missing()
        # option_pks = [x.id for x in self.option_list]
        # modified = False
        # for item in self.request.session[self.session_key].iteritems():
        #     for opt in item[1]['extra'].keys():
        #         if not opt in option_pks:
        #             del self.request.session[self.session_key][item[0]]['extra'][opt]
        #             modified = True
        # if modified:
        #     self.request.session.modified = True

    def prepare_data(self):
        super(CartWithOptions, self).prepare_data()
        if hasattr(self, 'option_list'):
            return None
        options_pks = sum(map(lambda x: x[1]['extra'].keys(), self.request.session[self.session_key].items()), [])
        self.option_list = []
        self.option_prices = {}
        if len(options_pks) > 0:
            self.option_list = self.option_model.objects.filter(pk__in=options_pks)
            self.option_prices = {x['id']: x['price'] for x in self.option_list.values('id', 'price')}

    def get_item_price(self, item):
        price = 0
        for opt in item['extra'].items():
            if opt[0] in self.option_prices:
                price += self.option_prices[opt[0]]
        return (price  * item['count']) + super(CartWithOptions, self).get_item_price(item)

    def get_with_products(self):
        item_list = super(CartWithOptions, self).get_with_products()
        for item in item_list:
            item['price_for_one'] = self.product_prices[item['id']]
            for opt in item['extra'].items():
                if opt[0] in self.option_prices:
                    item['price_for_one'] += self.option_prices[opt[0]]
        return item_list
