# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.validators import validate_email
from django import forms
from django.contrib.auth import get_user_model

def get_admin_emails():
    admins = get_user_model().objects.filter(is_superuser=True)
    admin_list = []
    for admin in admins:
        try:
            validate_email(admin.email)
            admin_list.append(admin.email)
        except forms.ValidationError:
            pass
    return ','.join(admin_list)


def replace_email_variables(template, variables):
    """ Replace variables on email template"""

    email = getattr(settings, 'DEFAULT_EMAIL_FROM', '')
    if not variables.has_key('DEFAULT_EMAIL_FROM'):
        try:
            validate_email(email)
            variables['DEFAULT_EMAIL_FROM'] = email
        except forms.ValidationError:
            raise RuntimeError("Проверить настройки email сейчас установлен email - \"%s\"" %
                    email)


    current_site = Site.objects.get_current()
    admin_emails = get_admin_emails()

    variables.update({
        'DOMAIN':              current_site.domain,
        'SITE_NAME':           current_site.name,
        'DEFAULT_SMS_FROM':    '',
        'ADMIN_EMAIL':         admin_emails,
        'ADMIN_EMAILS':        admin_emails,
        'ADMINS_EMAIL':        admin_emails,
    })

    for var, value in variables.iteritems():
        if not value:
            value = ''

        template.message = template.message.replace(u'#%s#' % var, unicode(value))
        template.subject = template.subject.replace(u'#%s#' % var, unicode(value))
        template.email_from = template.email_from.replace(u'#%s#' % var, unicode(value))
        template.email_to = template.email_to.replace(u'#%s#' % var, unicode(value))
        template.to = template.email_to.replace(u'#%s#' % var, unicode(value))

    return template


def replace_sms_variables(template, variables):
    """ Replace variables on sms template"""

    current_site = Site.objects.get_current()
    variables['DOMAIN'] = current_site.domain
    variables['SITE_NAME'] = current_site.name

    #variables['DEFAULT_SMS_FROM'] = settings.DEFAULT_SMS_FROM if settings.DEFAULT_SMS_FROM else ''
    variables['DEFAULT_SMS_FROM'] = ''

    for var, value in variables.iteritems():
        if not value:
            value = ''

        template.message = template.message.replace(u'#%s#' % var, unicode(value))
        template.to = template.to.replace(u'#%s#' % var, unicode(value))
        template.sender = template.sender.replace(u'#%s#' % var, unicode(value))

    return template
