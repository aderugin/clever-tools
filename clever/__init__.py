# -*- coding: utf-8 -*-
__import__('pkg_resources').declare_namespace(__name__)
VERSION = (0, 4, 0, '')

if VERSION[-1] != "final":  # pragma: no cover
    __version__ = '.'.join(map(str, VERSION))
else:  # pragma: no cover
    __version__ = '.'.join(map(str, VERSION[:-1]))
