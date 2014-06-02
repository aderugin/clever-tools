# -*- coding: utf-8 -*-

from UserDict import UserDict

class Enviroment(UserDict):
    def __init__(self):
        # Расположение зависимостей для проекта
        self.REQUIREMENTS_NAME = 'requirements.pip'

        # Расположение FastCGI скрипта для запуска и его перезапуска сервера
        self.DJANGO_WSGI_NAME = 'django-wrapper.fcgi'

        # Расположение внешнего репозитория для верстки, если отсуствует в False
        self.MARKUP_DIRECTORY = None

        # Расположение для бэкапа
        self.BACKUP_DIRECTORY = "cache/backup/db"

        # Название файла с концигурацией Django
        self.DJANGO_SETTINGS = None

        # Окружение тестового сервера
        self.STAGING_ENVIRONMENT = { }

        # Окружение рабочего сервера
        self.PRODUCTION_ENVIRONMENT = { }

        # Текущий репозиторий
        self.CLEVER_REVISION = 'master'

        # нужна ли установка bower
        self.IS_BOWER_INSTALL = True
