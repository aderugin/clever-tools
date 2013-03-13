# -*- coding: utf-8 -*-

import datetime
import time

from django import forms
from .models import *
from ..users.models import RikitaviUser
from cart import get_user_cart


class OrderForm(forms.ModelForm):
    request = None

    def __init__(self, request, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['user_name'].required = True
        self.fields['user_email'].required = True
        self.fields['user_phone'].required = True
        self.request = request

    class Meta:
        model = Order
        exclude = (
            'user',
            'status',
            'location',
            'delivery_cost',
            'delivery_date',
            'delivery_time',
            'total_cost',
            'total_cost_with_sale'
        )

        widgets = {
            'delivery': forms.HiddenInput,
            'payment': forms.HiddenInput,
            'adress': forms.Textarea(attrs={'cols': 30, 'rows': 4}),
            'comment': forms.Textarea(attrs={'cols': 30, 'rows': 4}),
        }

    def clean(self):
        cart = get_user_cart(self.request)
        cleaned_data = super(OrderForm, self).clean()
        confirm = self.data.get('confirm', False)
        password1 = self.data.get('password1', '')
        password2 = self.data.get('password2', '')
        delivery = self.cleaned_data.get('delivery')
        user_name = self.cleaned_data.get('user_name')
        user_email = self.cleaned_data.get('user_email')
        user_phone = self.cleaned_data.get('user_phone')
        today = datetime.datetime.today()

        # check location & delivery
        costs = LocationDeliveryCost.objects.filter(delivery=delivery, location=self.data.get('location'))
        if (costs.count() > 0):
            cost = costs.all()[0]
            try:
                free_delivery_from = float(cost.free_delivery_from)
            except:
                free_delivery_from = 0
            if (cart.get_total_cost() >= free_delivery_from and free_delivery_from > 0):
                self.cleaned_data['delivery_cost'] = 0
            else:
                self.cleaned_data['delivery_cost'] = float(cost.price)
        else:
            raise forms.ValidationError('location must be set')

        # delivery date & time
        if (self.data.get('delivery_date_radio', 'today') == 'today'):
            self.cleaned_data['delivery_date'] = today.strftime('%d.%m.%Y')
        else:
            self.cleaned_data['delivery_date'] = self.data.get('delivery_date', '')
            if datetime.datetime(
                *time.strptime(self.cleaned_data['delivery_date'], '%d.%m.%Y')[:6]
            ) < datetime.datetime(today.year, today.month, today.day):
                raise forms.ValidationError('error in date')

        self.cleaned_data['delivery_time'] = self.data.get('delivery_time', '')

        # confirmation
        if (confirm == 1):
            self.cleaned_data['need_confirm'] = True

        # user
        if (self.request.user.id):
            cleaned_data['user'] = self.request.user
        elif (self.data.get('create_user', False)):
            if (password1 != password2 or len(password1) < 6):
                raise forms.ValidationError('password')
            user_by_email = RikitaviUser.objects.filter(username=user_email)
            if (user_by_email.count() > 0):
                raise forms.ValidationError('user already exists')

        return cleaned_data

    def save(self, commit=True):
        instance = super(OrderForm, self).save(commit=False)
        instance.delivery_cost = self.cleaned_data['delivery_cost']
        instance.delivery_date = self.cleaned_data['delivery_date']
        instance.delivery_time = self.cleaned_data['delivery_time']
        instance.need_confirm = self.cleaned_data.get('need_confirm', False)
        instance.user = self.cleaned_data.get('user', None)
        instance.status = Order.NEW
        try:
            location = DeliveryLocation.objects.get(pk=int(self.data.get('location')))
        except:
            location = None
        instance.location = location.name if location else ''
        instance.save()
        return instance
