# -*- coding: utf-8 -*-
from clever.markup.extensions import FixtureExtension


class FormExtension(FixtureExtension):
    def process_data(self, data, metadata):
        import ipdb; ipdb.set_trace()
        return None
