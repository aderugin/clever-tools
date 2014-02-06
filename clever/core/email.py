# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from templated_emails.utils import send_templated_email
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from clever.notifier import send_message


def get_site_url(url):
    current_site = Site.objects.get_current()
    if current_site:
        return ''.join(['http://', current_site.domain, url])
    return ''


def get_frontend_view_url(instance):
    if hasattr(instance, 'get_absolute_url'):
        return get_site_url(instance.get_absolute_url())
    return ''


def get_backend_edit_url(instance):
    return get_site_url(reverse('admin:%s_%s_change' % (instance._meta.app_label, instance._meta.module_name), args=[instance.id]))


def send_message_when_created(template_name, admin=True, staff=True):
    def decorator(cls):
        def send_message_handler(instance, created, **kwargs):
            querypart = None
            if admin:
                querypart = Q(is_superuser=True)
            if staff:
                if querypart:
                    querypart = querypart | Q(is_staff=True)
                else:
                    querypart = Q(is_staff=True)

            if querypart and created:
                fields = {x.name: None for x in instance._meta.fields}
                for field in fields:
                    fields[field] = getattr(instance, field)
                if hasattr(instance, 'get_notifier_context'):
                    fields = instance.get_notifier_context(fields)
                users = get_user_model().objects.filter(querypart)
                for user in users:
                    fields['email'] = user.email
                    send_message(template_name, fields)
        post_save.connect(send_message_handler, sender=cls, weak=False)
        return cls

    return decorator

#-------------------------------------------------------------------------------
def send_create_email_to_managers(template_name, var_name='instance', admin=True, staff=True):
    ''' Декаратор для отправка письма на email при создании нового экземпляра модели '''

    def outer_wrapper(cls):
        def send_feedback_email(instance, created, **kwargs):
            querypart = None
            if admin:
                querypart = Q(is_superuser=True)
            if staff:
                if querypart:
                    querypart = querypart | Q(is_staff=True)
                else:
                    querypart = Q(is_staff=True)

            if querypart and created:
                users = get_user_model().objects.filter(querypart)
                email_lists = [user.email for user in users]
                email_lists = filter(lambda email: email is not None and len(email) > 0, email_lists)
                send_templated_email(email_lists, "emails/" + template_name, {
                    var_name: instance,

                    'admin_url': get_backend_edit_url(instance),
                    'view_url': get_frontend_view_url(instance),
                })

        post_save.connect(send_feedback_email, sender=cls, weak=False)
        return cls
    return outer_wrapper
