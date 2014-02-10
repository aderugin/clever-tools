# -*- coding: utf-8 -*-
import os
import json
import codecs
from jinja2 import nodes
from jinja2.ext import Extension
from sorl.thumbnail.shortcuts import get_thumbnail


# TODO: Загрузка fixtures по ключу use  [static]
# TODO: Загрузка данных по ключю from [dynamic]


class ExtendBlockExtension(Extension):
    ''' Custom {% extends_block <template> %} tag that allows templates
    to inherit from the ckan template futher down the template search path
    if no template provided we assume the same template name. '''

    tags = set(['extends_block'])

    def __init__(self, environment):
        super(ExtendBlockExtension, self).__init__(environment)
        try:
            self.searchpath = environment.loader.searchpath[:]
        except AttributeError:
            # this isn't available on message extraction
            pass

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        node = nodes.Extends(lineno)
        template_path = parser.filename

        # find where in the search path this template is from
        # index = 0
        # if not hasattr(self, 'searchpath'):
        #     return node
        # for searchpath in self.searchpath:
        #     if template_path.startswith(searchpath):
        #         break
        #     index += 1

        # get filename from full path
        # filename = template_path[len(searchpath) + 1:]

        # Providing template path vicolently deprecated
        env = self.environment
        if parser.stream.current.type != 'block_end':
            # Find info about base block
            block_name = parser.parse_expression().value
            # template_name = os.path.join('blocks', block_name, block_name + '.jhtml')
            template_name = block_name
            # template = env.get_template(template_name)
            # block_path = os.path.dirname(template.filename)

            # Find template assets
            # env.techs.find_techs(block_path, block_name)

        # set template
        node.template = nodes.Const(template_name)
        return node


class BaseExtension(Extension):
    ''' Base class for creating custom jinja2 tags.
    parse expects a tag of the format
    {% tag_name args, kw %}
    after parsing it will call _call(args, kw) which must be defined. '''

    def parse(self, parser):
        stream = parser.stream
        tag = stream.next()
        # get arguments
        args = []
        kwargs = []
        while not stream.current.test_any('block_end'):
            if args or kwargs:
                stream.expect('comma')
            if stream.current.test('name') and stream.look().test('assign'):
                key = nodes.Const(stream.next().value)
                stream.skip()
                value = parser.parse_expression()
                kwargs.append(nodes.Pair(key, value, lineno=key.lineno))
            else:
                args.append(parser.parse_expression())

        def make_call_node(*kw):
            return self.call_method('_call', args=[
                nodes.List(args),
                nodes.Dict(kwargs),
            ], kwargs=kw)

        return nodes.Output([make_call_node()]).set_lineno(tag.lineno)


class IncludeBlockExtension(BaseExtension):
    # a set of names that trigger the extension.
    tags = set(['include_block'])

    def _call(self, args, kwargs):
        env = self.environment

        # Find block template
        block_name = args[0]
        # template_name = os.path.join('blocks', block_name, block_name + '.jhtml')
        template_name = block_name
        template = env.get_template(template_name)
        block_path = os.path.dirname(template.filename)

        # Find block assets
        # env.techs.find_techs(block_path, block_name)

        # Find block data
        # try:
        #     template_json = env.get_template(os.path.join('blocks', block_name, block_name + '.json'))
        #     with codecs.open(template_json.filename, 'r', 'utf-8') as f:
        #         template_params = json.load(f, 'utf-8')
        # except IOError:
        template_params = {}
        template_params.update(kwargs)

        # Normal include
        return template.render(template_params)
