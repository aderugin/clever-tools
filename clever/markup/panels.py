# -*- coding: utf-8 -*-

from debug_toolbar.panels import Panel
from clever.markup import pages


class MarkupPanel(Panel):
    title = u'Верстка'
    template = 'markup/panel.html'

    def get_stats(self):
        stats = super(MarkupPanel, self).get_stats()
        manager = pages.Manager()
        stats.update({
            'manager': manager,
            'pages': manager.pages,
        })
        return stats
