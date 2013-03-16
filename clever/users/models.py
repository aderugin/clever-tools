# -*- coding: utf-8 -*-
#author: Semen Pupkov (semen.pupkov@gmail.com)

from django.contrib.auth.models import User, UserManager
from django.db import models


class CleverUser(User):

    class Meta:
        verbose_name = u'Пользователь'
        verbose_name_plural = u'Пользователи'

    bdate = models.DateField(verbose_name=u'День рождения', blank=True, null=True)
    initial_name = models.CharField(verbose_name=u'Отчество', blank=True, null=True, max_length=40)
    objects = UserManager()


    @property
    def fullname(self):
        return self.get_full_name()

    @fullname.setter
    def fullname(self, value):
        self.first_name = value

    def __unicode__(self):
        return unicode(self.get_full_name())

    def get_full_name(self):
        if not self.last_name:
            self.last_name = u""
        if not self.first_name:
            self.first_name = u""
        if not self.initial_name:
            self.initial_name = u""
        name = (self.last_name + " " + self.first_name + " " + self.initial_name)
        return name.strip()
