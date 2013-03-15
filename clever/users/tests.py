# -*- coding: utf-8 -*-
#author: Semen Pupkov (semen.pupkov@gmail.com)


from django.test import TestCase
from .forms import RegistrationForm
from .models import RikitaviUser
from django_any import any_model
from django.test.client import Client


class RegistrationTest(TestCase):

    form_data = {
        'email': 'me@me.ru',
        'name': u'Иванов Иван',
        'phone': '+790438017552',
        'password1': '123',
        'password2': '123'
    }

    def test_form_phone(self):

        form_data = self.form_data.copy()

        # Mobile
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

        # Not mobile
        form_data['phone'] = '+7(343)555-55-55'
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_user_exists(self):

        exists_email = 'me@me.ru'

        form_data = self.form_data.copy()

        # Check if user exists
        user = any_model(RikitaviUser, email=exists_email)
        user.save()

        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_not_valid_email(self):

        form_data = self.form_data.copy()
        form_data['email'] = 'me@'
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_redirect_in_view(self):
        c = Client()
        response = c.post('/account/register/', self.form_data)
        self.assertEqual(response.status_code, 302)
