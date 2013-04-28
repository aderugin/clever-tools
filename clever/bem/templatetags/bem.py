# -*- coding: utf-8 -*-
from django import template
from django.template.base import TemplateSyntaxError
# from django.template.base import VariableDoesNotExist
# from django.template.base import NodeList
from django.template.base import Node
# import re
# from django.conf import settings

from clever.bem.base import BemManager
from clever.bem.render import bemhtml_template
manager = BemManager()

#app = get_app('my_application_name')
#for model in get_models(app):
#    print model

register = template.Library()


class BemTemplateNode(Node):
    tag = None

    def __init__(self, tag):
        self.tag = tag

    def render(self, context):
        bemjson = self.tag.get_bemjson_context(context['request'], context)
        return bemhtml_template.render(bemjson)


@register.tag
def bem_template(parser, token):
    bits = token.contents.split()

    if len(bits) < 2:
        raise TemplateSyntaxError(u"'bem_template' должен иметь как минимум 1 аргумент - название тэга: %s" % token.contents)

    app_name, app_tag = bits[1].strip('\'\"').split('.')
    app = manager.get_app(app_name, app_tag)
    class_name = app_tag[0].upper() + app_tag[1:] + 'Tag'
    class_obj = getattr(app, class_name, None)
    if class_obj:
        tag = class_obj()
        return BemTemplateNode(tag)
    else:
        raise TemplateSyntaxError(u"'bem_template' Не найден класс %s в %s" % (class_name, app))
