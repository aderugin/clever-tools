# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from templated_emails.utils import send_templated_email
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site


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
                users = User.objects.filter(querypart)
                email_lists = [user.email for user in users]
                send_templated_email(email_lists, "emails/" + template_name, {
                    var_name: instance,

                    'admin_url': get_backend_edit_url(instance),
                    'view_url': get_frontend_view_url(instance),
                })

        post_save.connect(send_feedback_email, sender=cls, weak=False)
        return cls
    return outer_wrapper
