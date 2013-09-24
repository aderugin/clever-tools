# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns
from django.contrib import admin
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from .base import get_models
from .forms import create_form
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf.urls import url
from django.db import models

def show_site_settings(request):
    """
    Show site settings and edit
    """
    site = Site.objects.get_current()
    # Collect all forms
    form_collection = []
    for name, model in get_models().items():
        try:
            instance = model.objects.get(_site=site)
        except ObjectDoesNotExist:
            instance = None

        form_class = create_form(model)
        form_collection.append((form_class, instance, name, model._meta.verbose_name))

    has_file_field = False
    for item in form_collection[0][1]._meta.fields:
        if type(item) == models.FileField or type(item) == models.ImageField:
            has_file_field = True
            break

    # Initialise all the forms, in a dictionary that we can later use
    # as context
    forms = dict(
        ("%s_form" % name, (form_class(
            request.POST or None,
            request.FILES or None,
            instance=instance,
            prefix=name
        ), title))
        for form_class, instance, name, title in form_collection
    )

    # if all forms are valid, save all forms
    if all(form.is_valid() for form, title in forms.values()):
        for form, title in forms.values():
            form.save()

        # redirect to placement
        if request.POST.get('_save', None) is not None:
            return redirect(reverse('admin:index'))
        if request.POST.get('_continue', None) is not None:
            return redirect(reverse('admin:site_settings'))

    context = {
        'form_url': reverse('admin:site_settings'),
        'forms': forms.values(),
        'has_file_field': has_file_field
    }
    return render_to_response(
        'clever/settings/form.html', context,
        context_instance=RequestContext(request))


def get_admin_urls(default_urls):
    def wrapper():
        return patterns('',
            url(r'^site_settings/$', admin.site.admin_view(show_site_settings), name='site_settings')
        ) + default_urls()
    return wrapper

admin.site.get_urls = get_admin_urls(admin.site.get_urls)
