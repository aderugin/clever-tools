# -*- coding: utf-8 -*-
from django.db import models
from .utils import replace_email_variables, replace_sms_variables


class Notification(models.Model):

    class Meta:
        verbose_name = u'Событие'
        verbose_name_plural = u'События'

    name = models.CharField(max_length=100, verbose_name=u'Название')
    slug = models.SlugField(max_length=100)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.slug)

    @classmethod
    def send(cls, slug, variables):
        """
            Send message using defined backend
            :slug: String event slug
            :variables: dict
        """

        # TODO: Define backends from settings
        # TODO: Need dummy backend
        from .backends.email import DefaultEmailBackend
        from .backends.sms import SmsHostBackend

        try:
            notification = cls.objects.get(slug=slug)
        except:
            notification = None
            # TODO: Need exeption
            pass
        finally:
            # Send email notification
            if notification:
                for template in notification.templates.filter(active=True):
                    template = replace_email_variables(template, variables)
                    DefaultEmailBackend(template).send_message()

                # Send sms notification
                for template in notification.sms_templates.filter(active=True):
                    template = replace_sms_variables(template, variables)
                    SmsHostBackend(template).send_message()


class Variable(models.Model):

    class Meta:
        verbose_name = u'Переменная'
        verbose_name_plural = u'Переменные'

    name = models.CharField(max_length=100, verbose_name=u'Название')
    code = models.CharField(max_length=100)
    notification = models.ForeignKey(Notification, related_name='variables')

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.code)


class Template(models.Model):

    class Meta:
        verbose_name = u'Шаблон email сообщения'
        verbose_name_plural = u'Шаблоны email сообщений'

    notification = models.ForeignKey(Notification, related_name='templates', verbose_name=u'Событие')
    active = models.BooleanField(default=True, verbose_name=u'Активность')
    email_from = models.CharField(max_length=100, verbose_name=u'От кого', default="#DEFAULT_EMAIL_FROM#")
    email_to = models.CharField(max_length=200, verbose_name=u'Кому', help_text=u'Несколько адресатов можно указать через запятую')
    subject = models.CharField(max_length=200, verbose_name=u'Тема')
    message = models.TextField(verbose_name=u'Сообщение')


class SmsTemplate(models.Model):
    class Meta:
        verbose_name = u'Шаблон смс сообщения'
        verbose_name_plural = u'Шаблоны смс сообщений'

    def __unicode__(self):
        return str(self.pk)

    notification = models.ForeignKey(Notification, related_name='sms_templates', verbose_name=u'Событие')
    active = models.BooleanField(default=True, verbose_name=u'Активность')
    sender = models.CharField(u'Отправитель', max_length=100, default='#DEFAULT_SMS_FROM#')
    to = models.CharField(max_length=100, verbose_name=u'Кому')
    message = models.TextField(verbose_name=u'Сообщение', help_text=u'Длина сообщения ограничивается шлюзом, обычно 140 символов')
