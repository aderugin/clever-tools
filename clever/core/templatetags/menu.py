# -*- coding: utf-8 -*-
import urllib
from coffin import template
register = template.Library()


def is_equal_url(url, request, fully=False):
    paths = [
        # Create hostnames
        '%s://%s/' % ('https' if request.is_secure() else 'http', request.get_host()),
        '%s://%s' % ('https' if request.is_secure() else 'http', request.get_host()),
        '//%s/' % (request.get_host()),
        '//%s' % (request.get_host()),

        # Create absolute path
        '%s://%s%s' % ('https' if request.is_secure() else 'http', request.get_host(), request.path),
        '//%s%s' % (request.get_host(), request.path),
        '%s%s' % (request.get_host(), request.path),
        '%s' % (request.path),
    ]
    # import pprint
    # print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    # pprint.pprint(url)
    # pprint.pprint(paths)
    # print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    return url in paths


@register.object
def is_active_item(object, request, fully=False):
    # TODO: Add compare breadcrumbs
    if isinstance(object, (str, unicode)):
        url = object
    else:
        url = object.get_absolute_url()

    # breadcrumbs = getattr(request, 'breadcrumbs', [])
    # import ipdb; ipdb.set_trace()
    # for item in breadcrumbs:
    #     import ipdb; ipdb.set_trace()
    return is_equal_url(url, request)