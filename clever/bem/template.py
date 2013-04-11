# -*- coding: utf-8 -*-

from clever.bem import unicode_utils
from django.template.loader import BaseLoader
from django.conf import settings
from glob import glob
import os
import PyV8

TECHS = [
    '*.bemhtml.js',
    '*.priv.js'
]


class TemplateError(Exception):
    pass


class Template:
    ''' Шаблон BEM-tools '''

    def __init__(self, source):
        self.source = source

    def render(self, context):
        ''' Рендеринг шаблона BEMHTML '''
        ctx = PyV8.JSContext(self)
        with ctx:
            ctx.locals.context = context
            ctx.locals.env = self

            js_code = "\n".join([
                unicode_utils.js_escape_unicode(self.source),
                'var data = render(this.context, this.env);',
                'BEMHTML.apply(data);',
            ])

            # TODO: Catch exception and convert to TemplateError, for compleant with django_toolbar
            # TODO: Send signal about rendering for render, for compleant with django_toolbar
            return ctx.eval(js_code)
        return ""


class Loader(BaseLoader):
    ''' Загрузчик шаблонов BEM-tools '''
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        for dir in settings.TEMPLATE_DIRS:
            jsdata = []

            # Поиск техник для BEMHTML
            for tech in TECHS:
                for fname in glob(os.path.join(dir, template_name, tech)):
                    path = os.path.join(dir, fname)
                    import pprint
                    pp = pprint.PrettyPrinter(indent=4, depth=6)
                    pp.pprint(path)
                    try:
                        jsdata.append(open(path).read())
                    except IOError:
                        pass

            # Если файлы найдены возвращаем их
            if len(jsdata) > 0:
                return "\n".join(jsdata), template_name
        return None

    def load_template(self, template_name, template_dirs=None):
        source, origin = self.load_template_source(template_name, template_dirs)
        template = Template(source)
        return template, origin
