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
from clever.fabric import local_env
import os
import json

# Список экспортируемых функций
__all__ = [
    'staging',
    'production',
    'update',
    'install',
    'backup',
    'rollback',
    'migrate',
    'collect',
    'restart',
    'flush_cache',
    'deploy',
    'help',
    'active_env',
]


def active_env(name):
    """
    Подготовка окружения
    """
    env_params = local_env.get(name, None)
    if not local_env:
        raise RuntimeError("Не найдено окружение")

    # Имя пользователя от которого запущен проект
    env.user = env_params.get('user')

    # Хосты на которых расположен проект.
    env.hosts = env_params.get('host')

    # Папка в котором располагается проект
    env.root = env_params.get('root_dir')

    # Ветка по умолчанию для
    env.branch = env_params.get('branch')

    # Путь до virtualenv директории на серверах
    env.activate = env_params.get('venv')

    # Имя окружения
    env.name = name


@task
def staging():
    """
    Подготовка окружения тестового сервера
    """
    active_env('STAGING_ENVIRONMENT')


@task
def production():
    """
    Подготовка окружения рабочего сервера
    """
    active_env('PRODUCTION_ENVIRONMENT')


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
    if local_env.MARKUP_DIRECTORY:
        with lcd(local_env.MARKUP_DIRECTORY):
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

        if local_env.MARKUP_DIRECTORY:
            with cd(local_env.MARKUP_DIRECTORY):
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
            run('pip install -r ' + local_env.REQUIREMENTS_NAME)


@task
def backup():
    """Резервное копирование базы данных"""

    context = {
        'dump': backup_mysql(local_env.BACKUP_DIRECTORY),
        'source': get_head_hash(env.root),
        'markup': None,
    }

    if local_env.MARKUP_DIRECTORY:
        with cd(env.root):
            context['markup'] = get_head_hash(local_env.MARKUP_DIRECTORY)

    # Сохраняем информацию о текущем положении
    with cd(env.root):
        template = os.path.join(os.path.dirname(__file__), '.fabric', 'backup.json')
        output = os.path.join(local_env.BACKUP_DIRECTORY, 'backup.json')
        files.upload_template(template, output, context=context)


@task
def rollback():
    """Восстановление предыдущего состояния кода и базы данных"""
    # Загружаем информацию о точке востоновления
    input = os.path.join(local_env.BACKUP_DIRECTORY, 'backup.json')
    output = os.path.join(local_env.BACKUP_DIRECTORY, '%(host)s-%(path)s')
    with cd(env.root):
        fullname = operations.get(input, local_path=output)[0]
    with open(fullname) as json_data:
        data = json.load(json_data)

    # Восстановление исходных кодов
    with cd(env.root):
        git_revert(data['source'])
        if local_env.MARKUP_DIRECTORY:
            with cd(local_env.MARKUP_DIRECTORY):
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
    with cd(env.root):
        with prefix(env.activate):
            # Перезапуск приложения Django
            run('killall -u ' + env.user + ' ' + local_env.DJANGO_WSGI_NAME)


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
