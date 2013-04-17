# -*- coding: utf-8 -*-
# work around modules with the same name
from __future__ import absolute_import

from debug_toolbar.panels import DebugPanel
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _


class BemPanel(DebugPanel):
    name = 'Bem Templates'
    has_content = True

    def process_request(self, request):
        # instance.reset()
        pass

    def nav_title(self):
        return _('Bem Templates')

    def nav_subtitle(self):
        # duration = 0
        # calls = instance.calls()
        # for call in calls:
        #     duration += call['duration']
        # n = len(calls)
        # if (n > 0):
        #     return "%d calls, %0.2fms" % (n, duration)
        # else:
        #     return "0 calls"
        return ''

    def title(self):
        return _('BEM Templates')

    def url(self):
        return ''

    def content(self):
        context = self.context.copy()
        context.update({})

        return render_to_string('bem_toolbar/templates.html', context)
