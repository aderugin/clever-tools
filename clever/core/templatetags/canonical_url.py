# -*- coding: utf-8 -*-
from django import template
from django.template.base import TemplateSyntaxError
from django.template.base import TemplateSyntaxError
from django.template.base import VariableDoesNotExist
from django.template.base import Node
from urlparse import urlparse, parse_qs

register = template.Library()

class CanonicalUrlNode(Node):
    def __init__(self, canonical_url, paginator_var=None, page_var=None):
        self.paginator_var = paginator_var
        self.page_var = page_var
        self.canonical_url = canonical_url

    def render(self, context):
        # Получаем каноничный URL
        canonical_url = self.canonical_url.resolve(context)

        # Проверяем условия для каноничности
        is_non_canonical = False
        if self.paginator_var:
            paginator = self.paginator_var.resolve(context)
            if paginator:
                page = self.page_var.resolve(context)
                if page.has_previous():
                    is_non_canonical = True

        # Проверяем запрос
        if not is_non_canonical:
            request = context['request']
            if not request:
                raise VariableDoesNotExist("Request not provided to 'canonical_url' tag")
            is_non_canonical = (canonical_url != request.get_full_path())

        # Формируем каноничную ссылку
        if is_non_canonical:
            return '<link rel="canonical" href="%s" />' % canonical_url
        return ''


@register.tag
def canonical_url(parser, token):
    bits = token.contents.split()

    if len(bits) != 2 and len(bits) != 4:
        raise TemplateSyntaxError("'canonical_url' statements should have at least three varaible with canonical url and optional paginator and page object"
                                  ": %s" % token.contents)

    canonical_url = template.Variable(bits[1])
    if len(bits) == 4:
        paginator_var = template.Variable(bits[2])
        page_var = template.Variable(bits[3])
        return CanonicalUrlNode(canonical_url, paginator_var, page_var);
    else:
        return CanonicalUrlNode(canonical_url);

