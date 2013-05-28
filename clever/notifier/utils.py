# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.conf import settings


def replace_email_variables(template, variables):
    """ Replace variables on email template"""

    current_site = Site.objects.get_current()
    variables['DOMAIN'] = current_site.domain
    variables['SITE_NAME'] = current_site.name

    #variables['DEFAULT_EMAIL_FROM'] = settings.DEFAULT_EMAIL_FROM if settings.DEFAULT_EMAIL_FROM else ''
    variables['DEFAULT_SMS_FROM'] = ''

    for var, value in variables.iteritems():
        if not value:
            value = ''

        template.message = template.message.replace('#%s#' % var, value)
        template.subject = template.subject.replace('#%s#' % var, value)
        template.email_from = template.email_from.replace('#%s#' % var, value)
        template.email_to = template.email_to.replace('#%s#' % var, value)
        template.to = template.email_to.replace('#%s#' % var, value)

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

        template.message = template.message.replace('#%s#' % var, value)
        template.to = template.to.replace('#%s#' % var, value)
        template.sender = template.sender.replace('#%s#' % var, value)

    return template
