# -*- coding: utf-8 -*-

from clever.bem import unicode_utils
from django.template.loader import BaseLoader
from django.template.base import TemplateDoesNotExist
from django.template.base import NodeList
from django.conf import settings
from glob import glob
from django import template
import os
import PyV8

TECHS = [
    '*.bemhtml.js',
    '*.priv.js'
]


#class Console(PyV8.JSClass):
#    def log(self, text):
#        print text

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


class TemplateNode(template.Node):
    def __init__(self, template):
        self.template = template

    def render(self, context):
        return self.template.render(context)


class Template:
    ''' Шаблон BEM-tools '''

    def __init__(self, source, filename):
        self.source = source
        self.filename = filename

    def thumbnail(self, image, sizes, params):
        from sorl.thumbnail import get_thumbnail
        params = dict(params)
        if image:
            try:
                thumb = get_thumbnail(image, sizes, **params)
                return {
                    'width': thumb.width,
                    'height': thumb.height,
                    'is_portrait': thumb.is_portrait,
                    'ratio': thumb.ratio,
                    'url': thumb.url,
                }
            except Exception, e:
                # TODO: Write error to log
                return None
        return None

    def url(self, object, args=[], kwargs={}):
        # TODO: Check if string, then return settings
        # TODO: Check if url is model with method get_absolute_url, then call this method and return result
        if isinstance(object, str):
            from django.core.urlresolvers import reverse
            python_args = list(args)
            python_kwargs = dict(kwargs)
            return reverse(object, args=python_args, kwargs=python_kwargs)
        else:
            return object.get_absolute_url

    def render(self, context):
        ''' Рендеринг шаблона BEMHTML '''
        ctx = PyV8.JSContext(TemplateGlobal())
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
            try:
                return ctx.eval(js_code)
            except Exception, e:
                raise TemplateError(self.filename, e.args[0])
        return ""

    @property
    def nodelist(self):
        nodelist = NodeList()
        nodelist.append(TemplateNode(self))
        return nodelist


class Loader(BaseLoader):
    ''' Загрузчик шаблонов BEM-tools '''
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        for dir in settings.TEMPLATE_DIRS:
            jsdata = []
            included_file = None

            # merged.bemhtml.js
            path = os.path.join(dir, 'pages/merged/_merged.bemhtml.js')
            try:
                merged_benhtml = open(path).read()
            except IOError:
                continue

            # Поиск техник для BEMHTML
            for tech in TECHS:
                for fname in glob(os.path.join(dir, template_name, tech)):
                    path = os.path.join(dir, fname)
                    try:
                        jsdata.append(open(path).read())
                        included_file = path
                    except IOError:
                        pass

            # Если файлы найдены возвращаем их
            if len(jsdata) > 0:
                jsdata.append(merged_benhtml)
                return "\n".join(jsdata), included_file
        raise TemplateDoesNotExist

    def load_template(self, template_name, template_dirs=None):
        source, origin = self.load_template_source(template_name, template_dirs)
        template = Template(source, origin)
        return template, origin
