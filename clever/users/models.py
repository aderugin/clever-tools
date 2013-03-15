# -*- coding: utf-8 -*-
#author: Semen Pupkov (semen.pupkov@gmail.com)

from django.contrib.auth.models import User, UserManager
from django.db import models
from rikitavi.apps.exchange_1c.save_to_export import save_entry_to_export
from django.dispatch import receiver


class RikitaviUser(User):

    class Meta:
        verbose_name = u'Пользователь'
        verbose_name_plural = u'Пользователи'

    phone = models.CharField(max_length=20, verbose_name=u'Номер телефона', blank=True, null=True)
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

class UserChildren(models.Model):

    class Meta:
        verbose_name = u'Ребенок'
        verbose_name_plural = u'Дети'

    MALE = 'male'
    FEMALE = 'female'

    SEX_CHOICES = (
        (MALE, u'Мужской'),
        (FEMALE, u'Женский')
    )

    user = models.ForeignKey(RikitaviUser, related_name='childrens')
    name = models.CharField(u'Имя', max_length=200)
    sex = models.CharField(u'Пол', max_length=10, choices=SEX_CHOICES)
    bdate = models.DateField(verbose_name=u'День рождения', blank=True, null=True)

    def __unicode__(self):
        return self.name


@receiver(models.signals.post_save, sender=RikitaviUser)
def to_export(instance, **kwargs):
    save_entry_to_export(RikitaviUser, 'users',  instance.id)
