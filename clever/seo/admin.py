# -*- coding: utf-8 -*-
from rollyourown.seo.admin import get_inline
from rollyourown.seo.admin import register_seo_admin
from clever.seo.settings import CLEVER_SEO_CLASS
from clever.magic import load_class
from django.contrib import admin


METADATA_CLASS = load_class(CLEVER_SEO_CLASS)


def inject_seo_inline():
    '''
    Декоратор для добавления редактора в экземпляры моделей в админке
    '''
    def outer_wrapper(cls):

        inlines = list(getattr(cls, 'inlines', []))
        inlines.append(get_inline(METADATA_CLASS))
        cls.inlines = inlines
        return cls
    return outer_wrapper


# Register seo module in admin
register_seo_admin(admin.site, METADATA_CLASS)
