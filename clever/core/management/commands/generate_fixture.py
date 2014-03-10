# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from clever.core import fixture


# app = get_app('my_application_name')
# for model in get_models(app):
#     # do something with the model

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--cleanup', action='store_true', help='Remove old classes'),
    )

    def handle(self, source_file=None, *args, **kwargs):
        fixtures_classes = fixture.load_fixtures()
        fixture_actions = []

        def fixture_cleanup(info, progress):
            fixture_class = info['fixture']
            fixture_model = fixture_class.FACTORY_FOR
            fixture_name = info.get('title', None)
            if not fixture_name:
                fixture_name = fixture_model._meta.verbose_name_plural.title()

            progress(u"Delete all instances for %s" % fixture_name)
            fixture_model.objects.all().delete()

        def fixture_generate(info, progress):
            fixture_class = info['fixture']

            # Prepare data for fixtures
            fixture_name = info.get('title', None)
            if not fixture_name:
                fixture_model = fixture_class.FACTORY_FOR
                fixture_name = fixture_model._meta.verbose_name_plural.title()
            fixture_count = info.get('count', 100)

            # Generate fixtures
            progress(u"Generate %d instance(s) for %s" % (fixture_count, fixture_name))
            fixture_class.create_batch(fixture_count)

        if kwargs.get('cleanup', False):
            for info in fixtures_classes:
                fixture_actions.append((fixture_cleanup, info))

        for info in fixtures_classes:
            fixture_actions.append((fixture_generate, info))

        progress_count = 0
        progress_max = len(fixture_actions)
        def progress(message):
            print u"[%d/%d] %s" % (progress_count, progress_max, message)

        for action in fixture_actions:
            progress_count += 1
            action[0](action[1], progress)
