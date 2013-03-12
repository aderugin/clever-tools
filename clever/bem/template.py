# -*- coding: utf-8 -*-

from django.template.loader import BaseLoader
from django.conf import settings
from glob import glob
import os
import PyV8

TECHS = [
    '*.bemhtml.js',
    '*.priv.js'
]


class Template:
    def __init__(self, source):
        self.source = source

    def render(self, context):
        ctx = PyV8.JSContext(self)
        with ctx:
            ctx.locals.context = context
            ctx.locals.env = self

            js_code = "\n".join([
                self.source,
                'BEMHTML.apply(render(context, env));'
            ])
            return ctx.eval(js_code)
        return ""



class Loader(BaseLoader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        for dir in settings.TEMPLATE_DIRS:
            jsdata = []
            for tech in TECHS:
                for fname in glob(os.path.join(dir, template_name, tech)):
                    path = os.path.join(dir, fname)
                    try:
                        jsdata.append(open(path).read())
                    except IOError:
                        pass
                if len(jsdata) > 0:
                    return "\n".join(jsdata), template_name
        return None


    def load_template(self, template_name, template_dirs=None):
        source, origin = self.load_template_source(template_name, template_dirs)
        template = Template(source)
        import pdb; pdb.set_trace()
        return template, origin
