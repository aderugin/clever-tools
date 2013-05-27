# -*- coding: utf-8 -*-
from django import forms
from clever.store.models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('status', )
