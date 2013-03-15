# -*- coding: utf-8 -*-
import json
import datetime
import hashlib

from django.template.loaders.filesystem import Loader
from django.template import Context, Template
from django.views.generic import FormView, TemplateView, View
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from pytils import numeral

from .forms import *
from .cart import Cart
from .delivery import CalcDelivery
from rikitavi.apps.catalog.models import Item
from .models import *
# from templated_emails.utils import send_templated_email
# from rikitavi.apps.catalog.templatetags.pruma_catalog_tags import wrap_price
#from rikitavi.apps.actions.helpers import set_action_to_cart
#from rikitavi.apps.store.utils import update_offers_quantity
from .signals import order_submited
from ..catalog.models import price_formated


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Cart):
            return super(MyEncoder, self).default(obj)

        return obj.__dict__


def get_shopping_cart(request, cart_class=Cart):
    return request.session.get('cart', None) or cart_class()


def update_shopping_cart(request, cart):
    request.session['cart'] = cart


def add_items(request, items=None):
    if items == None:
        items = []
        for k in request.POST:
            if k[:4] == 'item':
                q = int(request.POST[k])
                if (q > 0):
                    items.append([int(k[5:]), q])
    for item in items:
        return add(request, item[0], item[1])


def add(request, item_id=None, quantity=None):

    if item_id == None:
        item_id = request.REQUEST.get('id')

    if quantity == None:
        quantity = int(request.REQUEST.get('quantity', 1))

    product = Item.objects.get(id=item_id)
    if product:
        cart = get_shopping_cart(request)
        cart.add_item(product, quantity)
        update_shopping_cart(request, cart)

    if request.is_ajax():
        count = cart.get_count_items()
        to_json_responce = dict()
        to_json_responce['price'] = str(cart.get_total_cost())
        to_json_responce['quantity'] = count
        to_json_responce['plural'] = numeral.choose_plural(count, (u"товар", u"товара", u"товаров"))
        return HttpResponse(json.dumps(to_json_responce), mimetype='application/json')
    else:
        return HttpResponseRedirect(request.GET.get('next'))


def buy(request, item_slug):
    '''
    Добавляет товар в корзину и делает
    редирект в неë
    '''
    template_name = 'store/cart.html'

    obj = Item.objects.get(slug=item_slug)
    quantity = request.GET.get('quantity', 1)

    cart = get_shopping_cart(request)

    cart.add_item(obj, quantity)
    update_shopping_cart(request, cart)

    ctx = {'cart': cart}

    return HttpResponseRedirect("/cart/")


def ctx_cart_page(request):
    cart = get_shopping_cart(request)
    delivery = CalcDelivery(cart.get_total_cost())

    for item in cart:
        item.cost = item.quantity * item.product.price

    ctx = {
            'cart': cart,
            'total_cost': cart.get_total_cost,
            'total_cost_with_delivery' : cart.get_total_cost() + delivery.get_cost(),
          }

    return ctx


class CartIndex(TemplateView):

    template_name = 'store/cart_index.html'

    def get(self, request, *args, **kwargs):
        cart = get_shopping_cart(self.request)
        if (cart.get_count_items() < 1):
            return HttpResponseRedirect('/')
        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CartIndex, self).get_context_data(**kwargs)
        cart = get_shopping_cart(self.request)
        products = Item.objects.filter(id__in=[item.product.id for item in cart])
        total_price = float()
        Deliverys = Delivery.objects.order_by('sort').prefetch_related('locationdeliverycosts', 'locationdeliverycosts__location', 'payments')

        locations = {}
        first_locations = None
        for delivery in Deliverys:
            delivery.sorted_payments = delivery.payments.order_by('sort')
            id = int(delivery.id)
            locations[delivery.id] = [{
            'text': u'Выберите город',
            'value': 0
            }]
            for cost in delivery.locationdeliverycosts.all():
                locations[delivery.id].append({
                    'text': cost.location.name,
                    'value': int(cost.location.id),
                    'free_delivery_from': float(cost.free_delivery_from) if cost.free_delivery_from else 0,
                    'price': float(cost.price)
                    })
            if (first_locations == None):
                first_locations = locations[delivery.id]

        time = datetime.datetime.today()
        if time.hour > 9 and time.hour < 14:
            context['hide_12_time'] = True
        elif time.hour > 14:
            context['hide_today'] = True

        cart = set_action_to_cart(cart)
        try:
            context['settings'] = StoreSettings.objects.all()[0]
        except:
            pass
        context['tomorow'] = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d.%m.%Y')
        context['user'] = self.request.user
        context['cart'] = cart
        context['products'] = products
        context['deliverys'] = Deliverys
        context['order_form'] = OrderForm(self.request)
        context['total_price'] = cart.total_cost_with_sale
        context['locations'] = json.dumps(locations)
        context['first_locations'] = first_locations
        return context


class CartModalNologin(TemplateView):

    template_name = 'store/cart_modal_nologin.html'

    def get_context_data(self, **kwargs):
        context = super(CartModalNologin, self).get_context_data(**kwargs)
        self.request.session['redirect_url'] = '/store/#order-form-start'
        return context


class CartModalCheck(FormView):

    form_class = OrderForm
    template_name = 'store/cart_modal_check.html'

    def get_context_data(self, **kwargs):
        context = super(CartModalCheck, self).get_context_data(**kwargs)
        return context

    def get_form(self, form_class):
        return form_class(self.request, **self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        cart = get_shopping_cart(self.request)
        cart = set_action_to_cart(cart)

        total_price = cart.total_cost_with_sale()
        total_price += form.cleaned_data.get('delivery_cost', 0)
        return self.render_to_response(self.get_context_data(cart=cart,form=form,total_price=total_price))

    def form_invalid(self, form):
        return HttpResponse(json.dumps({'status': 'ERROR', 'errors': form.errors}), mimetype='application/json')


class CartModalCheckout(CartModalCheck):

    def form_valid(self, form):
        cart = get_shopping_cart(self.request)
        cart = set_action_to_cart(cart)

        if cart.is_empty():
            return HttpResponse(json.dumps({'redirect_url': '/'}))

        order = form.save(commit=False)
        order.total_cost = cart.get_total_cost()
        order.total_cost_with_sale = cart.total_cost_with_sale()

        if (len(order.payment.gateaway) > 0):
            order.total_cost = order.total_cost * 1.05
            order.total_cost_with_sale = order.total_cost_with_sale * 1.05

        order.save()

        # Подарок
        if cart.gift:
            gift_order_item = OrderItem()
            gift_order_item.order = order
            gift_order_item.sale = 100
            gift_order_item.quantity = 1
            gift_order_item.price = cart.gift.price
            gift_order_item.catalog_item_id = cart.gift.id
            gift_order_item.save()

        if order.pk:
            for cart_item in cart:
                order_item = OrderItem()
                order_item.order = order
                order_item.catalog_item_id = cart_item.product.id
                order_item.quantity = cart_item.quantity
                order_item.price = cart_item.product.price
                order_item.sale = cart_item.sale
                order_item.save()

        self.request.session['cart'] = None
        update_offers_quantity(order)

        order_submited.send(sender=order, order=order)

        return HttpResponse(json.dumps({'redirect_url': reverse('order_success')}), mimetype='application/json')


class AjaxDeliveryDate(View):

    def get(self, request, *args, **kwargs):
        time = datetime.datetime.today()
        today = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
        if (self.request.GET.get('day', 'today') == 'today'):
            needle = today
        else:
            needle = datetime.datetime.strptime(self.request.GET.get('date', False), '%d.%m.%Y')
        if (needle < today):
            data = {'status': 'ERROR'}
        elif (needle > today):
            data = {'options': ['c 12.00 - до 16.00', 'c 17.00 - до 21.00']}
        else:
            if time.hour > 9 and time.hour < 14:
                data = {'options': ['c 17.00 - до 21.00']}
            elif time.hour > 14:
                data = {'status': 'ERROR'}
        return HttpResponse(json.dumps(data), mimetype='application/json')

class RobokassaResult(View):

    def get(self, request, *args, **kwargs):
        InvId = request.GET.get('InvId', None)
        OutSum = request.GET.get('OutSum', None)
        remote_crc = request.GET.get('SignatureValue', '').upper()

        if (InvId == None):
            return HttpResponse('ERROR: NOT SET InvId')

        if (OutSum == None):
            return HttpResponse('ERROR: NOT SET OutSum')

        if (remote_crc == ''):
            return HttpResponse('ERROR: NOT SET SignatureValue')

        order_obj = Order.objects.filter(id=InvId,status=Order.CONFIRM_WAIT_ONLINE_PAYMENT).all()
        if (order_obj.count() > 0):

            order_obj = order_obj[0]
            md5 = hashlib.md5()
            md5.update(str(OutSum) + ':' + str(InvId) + ':' + order_obj.mrchpass2)
            local_crc = md5.hexdigest().upper()
            if (local_crc == remote_crc):
                order_obj.status = Order.CONFIRM_ONLINE_PAYMENT
                order_obj.save()
                return HttpResponse('OK' + str(InvId))
            else:
                return HttpResponse('ERROR: CRC NOT VALID')
        else:
            return HttpResponse('ERROR: ORDER NOT FOUND')



def clear_cart(request):
    '''
    Полностью очищает корзину
    '''
    request.session['cart'] = None
    return HttpResponseRedirect(reverse('catalog_index'))


def update_cart_item(request):
    """ Обновляет количество элемента в корзине """

    itemid = request.GET.get('itemid')
    quantity = request.GET.get('quantity')
    cart = get_shopping_cart(request)
    new_item_vals = cart.update_item_quantity(itemid, quantity)
    new_item_vals['new_cost'] = price_formated(new_item_vals['new_cost'])
    update_shopping_cart(request, cart)

    cart = set_action_to_cart(cart)
    total = cart.get_total_cost() - float(cart.sale_ammount)
    count = cart.get_count_items()

    ctx_to_json = {
        'discounts_estimated': [],
        'new_item_vals' : new_item_vals,
        'total_cost': price_formated(float(cart.total_cost_with_sale())),
        'quantity': count,
        'plural': numeral.choose_plural(count, (u"товар", u"товара", u"товаров")),
        'gift': None,
        'sale_ammount': price_formated(cart.get_discount()),
        'prices': []
    }


    for discount in cart.discounts:
        if (total >= float(discount.price)):
            ctx_to_json['discounts_estimated'].append(0)
        else:
            ctx_to_json['discounts_estimated'].append(float(discount.price) - total)

    for item in cart.items:
        ctx_to_json['prices'].append({
            'itemid':  item.itemid,
            'sale': item.sale,
            'new_price': float(item.total_price_wosale)
        })

    if cart.gift:
        loader = Loader()
        source, path = loader.load_template_source('store/_gift_row.html')
        t = Template(source)
        c = Context({'gift': cart.gift})
        gift_row_html = t.render(c)
        ctx_to_json['gift'] = gift_row_html

    return HttpResponse(json.dumps(ctx_to_json), mimetype='application/json')

def remove_from_cart(request, cart_item_id):
    '''
    Удяляет итем из корзины
    '''

    cart = get_shopping_cart(request)
    cart.remove_item(cart_item_id)

    update_shopping_cart(request, cart)

    return HttpResponseRedirect(reverse('store_cart'))

