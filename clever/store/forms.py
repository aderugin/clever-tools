# -*- coding: utf-8 -*-
from clever.magic import get_model_by_name
from django import forms


def get_product(content_type, id):
    model_class = get_model_by_name(content_type)
    if not model_class:
        raise forms.ValidationError('Not found product to cart')
    return model_class.objects.get(id=id)


class CartItemForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)
    product_id = forms.IntegerField(widget=forms.HiddenInput)

    count = forms.IntegerField(min_value=0, required=False)

    def clean(self):
        cleaned_data = super(CartItemForm, self).clean()

        # get product instance
        content_type = cleaned_data.pop('content_type')
        product_id = cleaned_data.pop('product_id')
        cleaned_data['product'] = get_product(content_type, product_id)

        # options
        options = {}
        for key in cleaned_data.keys():
            if key not in ['count', 'product']:
                options[key] = cleaned_data.pop(key)
        cleaned_data['options'] = options
        return cleaned_data