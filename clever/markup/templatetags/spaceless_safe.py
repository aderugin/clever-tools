from django.utils.functional import allow_lazy
from django.utils import six
from coffin.template.library import Library
from jinja2 import Markup
from jinja2.ext import Extension
from jinja2 import nodes
import re


def strip_spaces_between_tags(value):
    from django.utils.html import force_text
    """Returns the given HTML with spaces between tags removed."""
    return re.sub(r'>\s+<', Markup('><'), force_text(value))
strip_spaces_between_tags = allow_lazy(strip_spaces_between_tags, six.text_type)

class SpacelessSafeExtension(Extension):
    """Removes whitespace between HTML tags, including tab and
    newline characters.

    Works exactly like Django's own tag.
    """

    tags = set(['spaceless_safe'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endspaceless_safe'], drop_needle=True)
        return nodes.CallBlock(
            self.call_method('_strip_spaces', [], [], None, None),
            [], [], body,
        ).set_lineno(lineno)

    def _strip_spaces(self, caller=None):
        return strip_spaces_between_tags(caller().strip())

register = Library()

register.tag(SpacelessSafeExtension)
