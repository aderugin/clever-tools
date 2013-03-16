# -*- coding: utf-8 -*-
#author: Semen Pupkov (semen.pupkov@gmail.com)

from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import admin
from .models import CleverUser, UserChildren
from django.utils.translation import ugettext_lazy as _


class CleverUserChangeForm(UserChangeForm):

    class Meta:
        model = CleverUser


class CleverUserAdmin(UserAdmin):
    form = CleverUserChangeForm
    list_display = ('username', 'last_name', 'first_name', 'initial_name',
                    'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
                              'first_name', 'last_name', 'initial_name', 'email', 'bdate'
                              )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
         'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
    )

    inlines = [UserChildrenAdminInline]

admin.site.unregister(User)
admin.site.register(CleverUser, CleverUserAdmin)
