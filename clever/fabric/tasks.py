# -*- coding: utf-8 -*-
from fabric.api import task
from fabric.api import run
from fabric.api import local
from fabric.api import env
from fabric.api import cd
from fabric.api import lcd
from fabric.api import prefix
from fabric.api import hide
from fabric.contrib import files
from fabric import operations
import os
import json

### TODO: REFACTORING THIS!!!

# Расположение зависимостей для проекта
REQUIREMENTS_NAME = 'reqs_deps.txt'

# Расположение FastCGI скрипта для запуска и его перезапуска сервера
DJANGO_WSGI_NAME = 'django-wrapper.fcgi'

# Расположение внешнего репозитория для верстки, если отсуствует в False
MARKUP_DIRECTORY = "./poleroyal/static/proyal"

# Расположение для бэкапа
BACKUP_DIRECTORY = "cache/backup/db/"

# Название файла с концигурацией Django
DJANGO_SETTINGS = 'poleroyal.settings'

@task
def staging():
    """
    Подготовка окружения тестового сервера
    """
    # Имя пользователя от которого запущен проект
    env.user = 'root'

    # Хосты на которых расположен проект.
    env.hosts = ['root@109.120.139.125']

    # Папка в котором располагается проект
    env.root = "/hosting/paleroyal.placetest.ru/poleroyal"

    # Ветка по умолчанию для
    env.branch = "master"

    # Путь до virtualenv директории на серверах
    env.activate = 'source /hosting/paleroyal.placetest.ru/venv/bin/activate'

    # Имя окружения
    env.name = 'staging'


@task
def production():
    """
    Подготовка окружения рабочего сервера
    """
    # Имя пользователя от которого запущен проект
    env.user = 'u25614'

    # Хосты на которых расположен проект.
    env.hosts = ['u25614@u25614.netangels.ru']

    # Папка в котором располагается проект
    env.root = "/home/u25614/paleroyal.ru/paleroyal-django"

    # Ветка по умолчанию для
    env.branch = "master"

    # Путь до virtualenv директории на серверах
    env.activate = 'source //home/u25614/python/bin/activate'

    # Имя окружения
    env.name = 'production'

    global REQUIREMENTS_NAME
    REQUIREMENTS_NAME = 'reqs.txt'


@task
def update(branch=None, force=False):
    """
    Обновление исходного кода из ветки

    Аргументы:
        - :branch: Ветка из которой берутся изменения, по умолчанию текущий для окружения
    """
    if branch is None:
        branch = env.branch

    # Отправляем локальные изменения в приложении на сервер
    local("git push origin " + branch)

    # Отправляем локальные изменения в верстке на сервер
    if MARKUP_DIRECTORY:
        with lcd(MARKUP_DIRECTORY):
            local("git push origin master")

    with cd(env.root):
        # Обновляем бранчи если надо
        if branch != env.branch:
            run('git fetch --all')

        if force:
            run('git reset --hard HEAD')

        # Перемещаем изменения из репозитория в локальную папку
        run('git pull origin ' + branch)
        run('git checkout ' + branch)

        # Обновляем исходный код для статических файлов
        #run('git submodule update --init')

        if MARKUP_DIRECTORY:
            with cd(MARKUP_DIRECTORY):
                if force:
                    run('git fetch --all')
                    run('git reset --hard origin/master')
                else:
                    run('git pull origin master')


@task
def install(branch=None):
    """
    Установка зависимостей

    Аргументы:
        - :branch: Ветка из которой берутся изменения, по умолчанию текущий для окружения
    """
    with cd(env.root):
        # Обновляем зависимости для проекта
        with prefix(env.activate):
            run('pip install -r ' + REQUIREMENTS_NAME)


@task
def backup():
    """Резервное копирование базы данных"""

    context = {
        'dump': backup_mysql(BACKUP_DIRECTORY),
        'source': get_head_hash(env.root),
        'markup': None,
    }

    if MARKUP_DIRECTORY:
        with cd(env.root):
            context['markup'] = get_head_hash(MARKUP_DIRECTORY)

    # Сохраняем информацию о текущем положении
    with cd(env.root):
        template = os.path.join(os.path.dirname(__file__), '.fabric', 'backup.json')
        output = os.path.join(BACKUP_DIRECTORY, 'backup.json')
        files.upload_template(template, output, context=context)


@task
def rollback():
    """Восстановление предыдущего состояния кода и базы данных"""
    # Загружаем информацию о точке востоновления
    input = os.path.join(BACKUP_DIRECTORY, 'backup.json')
    output = os.path.join(BACKUP_DIRECTORY, '%(host)s-%(path)s')
    with cd(env.root):
        fullname = operations.get(input, local_path=output)[0]
    with open(fullname) as json_data:
        data = json.load(json_data)

    # Восстановление исходных кодов
    with cd(env.root):
        git_revert(data['source'])
        if MARKUP_DIRECTORY:
            with cd(MARKUP_DIRECTORY):
                git_revert(data['markup'])

    # Восстановление базы данныx
    revert_mysql(data['dump'])


@task
def migrate(merge=False):
    """
    Миграция изменений схемы в БД
    """
    append = ""
    if merge:
        append = " --merge"

    with cd(env.root):
        with prefix(env.activate):
            # Обновления БД в соответствии с джанго
            run('python manage.py syncdb')

            # Мигрируем изменения в БД
            run('python manage.py migrate' + append)


@task
def collect():
    """
    Сборка и обновление статических файлов проекта
    """
    # Собираем статические файлы
    with cd(env.root):
        with prefix(env.activate):
            run('python manage.py collectstatic --noinput')


@task
def restart():
    """
    Перезапуск приложения
    """
    if env.name == 'staging':
        run('service apache2 restart')
    else:
        with cd(env.root):
            with prefix(env.activate):
                # Перезапуск приложения Django
                run('killall -u ' + env.user + ' ' + DJANGO_WSGI_NAME)


@task
def flush_cache():
    """
    Сбросить кэш Reddis'а
    """
    run("echo 'FLUSHALL' | redis-cli")


@task
def deploy(branch=None, flush=False):
    """
    Выполнить полное развертывание приложения на сервере

    Аргументы:
        - :branch: Ветка из которой берутся изменения, по умолчанию текущий для окружения
        - :flush:  Сбросить кэш Reddis'а
    """
    backup()
    update(branch)
    install()
    migrate()
    collect()
    restart()
    if flush:
        flush_cache()


@task(default=True)
def help():
    """
    Выводит эту справку
    """

    print """
Основные команды:

    fab --list                  список всех команд
    fab -d <команда>            информация о команде
    fab staging <команда>       выполнение команды на тестовом сервере
    fab production <команда>    выполнение команды на рабочем сервере

Обновить полностью тестовый сервер без сброса кэша:

    fab staging deploy:production

Обновить полностью тестовый сервер со сбросом кэша:

    fab staging deploy:production,flush:1

    """

    with hide('status', 'aborts', 'warnings', 'running', 'stderr', 'user'):
        local("fab --list")

    import fabric.state
    fabric.state.output.status = False


def get_head_hash(path):
    """Получить хэш текущего коммита для GIT"""
    with cd(path):
        with hide('output', 'running'):
            return run('git rev-parse HEAD').split()[0]

def git_revert(commit):
    """Откат изминений в репозитории"""
    # reset the index to the desired tree
    run("git reset %s" % commit)
    # move the branch pointer back to the previous HEAD
    run("git reset --soft HEAD@{1}")
    #run("git commit -m 'Revert to %s'" % commit)
    # Update working copy to reflect the new commit
    run("git reset --hard")

def get_mysql_params():
    console_line = "DJANGO_SETTINGS_MODULE=%s python -c \"from django.conf import settings; print settings.DATABASES['default']['%s']\""
    with cd(env.root):
        with prefix(env.activate):
            with hide('output', 'running'):
                params = {
                    'db_user': run(console_line % (DJANGO_SETTINGS, "USER")),
                    'db_pass': run(console_line % (DJANGO_SETTINGS, "PASSWORD")),
                    'db_name': run(console_line % (DJANGO_SETTINGS, "NAME")),
                }
    return params

def backup_mysql(path):
    from datetime import datetime
    dump_file = str(datetime.now()).replace(':', '_').replace(' ', '_') + '.sql'
    fullname = os.path.join(path, dump_file)

    params = get_mysql_params()
    with cd(env.root):
        run('mysqldump -u%s -p%s %s > %s' % (
            params['db_user'],
            params['db_pass'],
            params['db_name'],
            fullname
        ))
    return fullname

def revert_mysql(fullname):
    params = get_mysql_params()
    with cd(env.root):
        run('mysql -u%s -p%s %s < %s' % (
            params['db_user'],
            params['db_pass'],
            params['db_name'],
            fullname
        ))
