# -*- coding: utf-8 -*-
import re

ESCAPABLE = re.compile(r'([^\x00-\x7f])')
HAS_UTF8 = re.compile(r'[\x80-\xff]')


def _js_escape_unicode_re_callack(match):
    s = match.group(0)
    n = ord(s)
    if n < 0x10000:
        return r'\u%04x' % (n,)
    else:
        # surrogate pair
        n -= 0x10000
        s1 = 0xd800 | ((n >> 10) & 0x3ff)
        s2 = 0xdc00 | (n & 0x3ff)
        return r'\u%04x\u%04x' % (s1, s2)

def js_escape_unicode(s):
    """Return an ASCII-only representation of a JavaScript string"""
    if isinstance(s, str):
        if HAS_UTF8.search(s) is None:
            return s
        s = s.decode('utf-8')
    return str(ESCAPABLE.sub(_js_escape_unicode_re_callack, s))
