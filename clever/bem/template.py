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

            # merged.bemhtml.js
            path = os.path.join(dir, 'pages/merged/merged.bemhtml.js')
            print "Include:", path
            try:
                jsdata.append(open(path).read())
                print "Include is success:", path
            except IOError:
                pass

            #
            for tech in TECHS:
                print "Glob:", os.path.join(dir, template_name, tech)
                for fname in glob(os.path.join(dir, template_name, tech)):
                    path = os.path.join(dir, fname)
                    print "Include:", path
                    try:
                        jsdata.append(open(path).read())
                        print "Include is success:", path
                    except IOError:
                        pass
                if len(jsdata) > 0:
                    return "\n".join(jsdata), template_name
        return None

    def load_template(self, template_name, template_dirs=None):
        source, origin = self.load_template_source(template_name, template_dirs)
        template = Template(source)
        return template, origin
