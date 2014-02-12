# -*- coding: utf-8 -*-
import os
import json
import codecs
from jinja2 import nodes
from jinja2.ext import Extension
from sorl.thumbnail.shortcuts import get_thumbnail
from clever import fixture

class LoadFixtureExtension(Extension):
    tags = set(['load_fixture'])

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = []
        fixture_name = parser.parse_expression()

        if fixture_name is not None:
            args.append(fixture_name)

        import ipdb; ipdb.set_trace()
        return nodes.CallBlock(self.call_method('_load_fixture', args), [], [], []).set_lineno(lineno)

    def _load_fixture(self, fixture_name, caller):
        import ipdb; ipdb.set_trace()
        fixtures = fixture.load_fixture(fixture_name)
        # lexer = None
        # formatter = HtmlFormatter(linenos='table')
        # content = caller()

        # if fixture_name is None:
        #     lexer = guess_lexer(content)
        # else:
        #     lexer = get_lexer_by_name(fixture_name)

        # return highlight(content, lexer, formatter)
