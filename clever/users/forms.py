# -*- coding: utf-8 -*-
#author: Vasiliy Sheredeko (piphon@gmail.com)

from .models import RikitaviUser
from .models import UserChildren
from registration.forms import RegistrationFormUniqueEmail
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm


class UserEditForm(ModelForm):
    class Meta:
        model = RikitaviUser
        fields = ("fullname", "email", "bdate", "phone")

    fullname = forms.CharField(widget=forms.TextInput(), label=u"Фамилия Имя Отчество")

    def __init__(self, *args, **kw):
        instance = kw.get('instance', None)
        if instance:
            if not 'initial' in kw:
                kw['initial'] = {}
            kw['initial']['fullname'] = instance.get_full_name()
        super(UserEditForm, self).__init__(*args, **kw)

    def clean(self):
        super(UserEditForm, self).clean()
        names = self.cleaned_data.pop('fullname').strip().split(" ", 3)
        if len(names) == 0:
            last_name, first_name, initial_name = (None, None, None)
        elif len(names) == 1:
            last_name, first_name, initial_name = names + (None, None)
        elif len(names) == 2:
            last_name, first_name, initial_name = names + (None,)
        elif len(names) == 3:
            last_name, first_name, initial_name = names
        self.cleaned_data['last_name'] = last_name
        self.cleaned_data['first_name'] = first_name
        self.cleaned_data['initial_name'] = initial_name
        return self.cleaned_data

    def save(self):
        instance = super(UserEditForm, self).save(commit=False)
        instance.last_name = self.cleaned_data['last_name']
        instance.first_name = self.cleaned_data['first_name']
        instance.initial_name = self.cleaned_data['initial_name']
        instance.save()
        return instance


class RegistrationForm(RegistrationFormUniqueEmail):

    def __init__(self, *args, **kw):
        super(RegistrationFormUniqueEmail, self).__init__(*args, **kw)
        del(self.fields['username'])

        self.fields['email'].label = u'Email'
        self.fields['password1'].label = u'Введите пароль'
        self.fields['password2'].label = u'Подтвердите пароль'

        for f_name, f in self.fields.iteritems():
            f.widget.attrs['placeholder'] = f.label

    name = forms.CharField(widget=forms.TextInput(), label=u"Фамилия Имя Отчество")
    phone = forms.CharField(widget=forms.TextInput(), label=u"Телефон")

    def clean_phone(self):
        """ Phone number validation """
        phone = self.cleaned_data.get('phone')
        if len(phone) != 13:
            raise forms.ValidationError(u"Неверный формат телефона")
        return phone

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if RikitaviUser.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(u'Пользователь с таким email уже существует')
        return self.cleaned_data['email']


class AuthenticationFormByEmail(AuthenticationForm):
    """
    Форма авторизации
    """
    email = forms.EmailField(widget=forms.TextInput(
        attrs=dict(maxlength=75)), label="E-mail")
    remember_me = forms.BooleanField(widget=forms.CheckboxInput(
    ), label=u'Запомнить меня', required=False)

    def __init__(self, *args, **kwargs):
        result = super(
            AuthenticationFormByEmail, self).__init__(*args, **kwargs)
        del self.fields['username']
        self.fields.keyOrder = ['email', 'password']

        self.fields['email'].widget.attrs['placeholder'] = u'Электронная почта'
        self.error_messages['invalid_login'] = 'Не верный email или пароль'
        return result

    def clean(self):

        try:
            user = RikitaviUser.objects.get(email=self.cleaned_data.get('email'))
            self.cleaned_data['username'] = user.username
        except:
            self.cleaned_data['username'] = self.cleaned_data.get('email')
        return super(AuthenticationFormByEmail, self).clean()


class UserChangePasswordForm(PasswordChangeForm):
    pass


class ChildrenForm(ModelForm):
    class Meta:
        model = UserChildren
        fields = ('name', 'sex', 'bdate',)
