# -*- coding: utf-8 -*-

from clever.bem import unicode_utils
from django.template.loader import BaseLoader
from django.template.base import Node
from django.template.base import NodeList
from django.template.base import TemplateDoesNotExist
from django.conf import settings
from decimal import Decimal
from glob import glob
import os
import PyV8
import locale

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

TECHS = [
    '*.bemhtml.js',
    # '*.priv.js'
]


class Console(PyV8.JSClass):
    def __init__(self):
        import pprint
        self.pp = pprint.PrettyPrinter(indent=4, depth=6)

    def log(self, text):
        self.pp.pprint(text)

    def dir(self, text):
        self.pp.pprint(dir(text))


class TemplateGlobal(PyV8.JSClass):
    console = Console()


class TemplateError(StandardError):
    def __init__(self, *args, **kwargs):
        super(TemplateError, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u"Ошибка JavaScript в файле '%s':\n '%s'" % (self.args[0], unicode(self.args[1]))


class Template:
    ''' Шаблон BEM-tools '''

    def __init__(self, source, filename):
        self.source = source
        self.filename = filename

    def render(self, data):
        ''' Рендеринг шаблона BEMHTML '''
        ctx = PyV8.JSContext(TemplateGlobal())
        with ctx:
            ctx.locals.data = data
            ctx.locals.env = self

            js_code = "\n".join([
                unicode_utils.js_escape_unicode(self.source),
                'BEMHTML.apply(this.data);',
            ])

            # TODO: Catch exception and convert to TemplateError, for compleant with django_toolbar
            # TODO: Send signal about rendering for render, for compleant with django_toolbar
            try:
                return ctx.eval(js_code)
            except Exception, e:
                raise TemplateError(self.filename, e.args[0])
        return ""


def load_template_source():
    for dir in settings.TEMPLATE_DIRS:
        jsdata = []
        included_file = None

        # merged.bemhtml.js
        path = os.path.join(dir, 'pages/merged/_merged.bemhtml.js')
        try:
            merged_benhtml = open(path).read()
            return Template(merged_benhtml, path)
        except IOError:
            continue
    raise TemplateDoesNotExist
bemhtml_template = load_template_source()
