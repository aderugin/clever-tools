# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from clever.markup.pages import Page
from clever.markup.pages import Manager
import codecs
import os
import logging


# TODO: Копирование всех статических файлов в папку Build
# TODO: Настройка папки Build из django settings
# TODO: Создание индекса страниц [index.html]
# TODO: Добавление авторизированного пользователя в request
class Command(BaseCommand):
    help = 'Build static markup'
    can_import_settings = True

    def handle(self, *args, **options):
        # Create log
        log = logging.getLogger('clever.markup')

        # Change settings for output
        from django.conf import settings
        settings.STATIC_URL = ''
        settings.DEBUG = False
        settings.COMPRESS_ENABLED = True
        settings.COMPRESS_URL = ''

        # Create page manager
        manager = Manager()

        # Render pages
        for page in manager.pages.values():
            log.info('Save page %s [%s] to file %s', page.id, page.title, page.output_name)

            filename = os.path.join(settings.STATIC_ROOT, page.output_name)
            with codecs.open(filename, 'w+', 'utf-8') as f:
                f.write(manager.render_page(page))

        # Render pages index
        filename = os.path.join(settings.STATIC_ROOT, "index.html")
        with codecs.open(filename, 'w+', 'utf-8') as f:
            log.info('Save pages index [%s] to file %s', u'', 'index.html')
            f.write(manager.render_index())
