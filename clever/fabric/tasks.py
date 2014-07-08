# -*- coding: utf-8 -*-
from fabric.api import task
from fabric.api import run
from fabric.api import local
from fabric.api import env
from fabric.api import cd
from fabric.api import lcd
from fabric.api import prefix
from fabric.api import hide
from fabric.api import get
from fabric.api import settings
from fabric.contrib import files
from fabric.utils import abort
from fabric import operations
from clever.fabric import local_env
from clever.fabric.utils import backup_mysql, backup_postgre
from clever.fabric.utils import get_head_hash
from clever.fabric.utils import git_revert
from clever.fabric.utils import revert_mysql
from clever.fabric.utils import get_django_setting
from clever.fabric.utils import install_packages
from clever.fabric.utils import is_python27
from clever.fabric.utils import generate_secret_key
from fabric.colors import red, green, blue
import os
import json


# Список экспортируемых функций
__all__ = [
    'staging',
    'production',

    'backup',
    'rollback',

    'copy_backup',
    'copy_media',

    'update',
    'install',
    'migrate',
    'collect',
    'restart',

    # 'active_env',
    'flush_cache',
    'import_xml',

    'deploy',

    'help',
]


def is_active_env(func):
    def wrapper(*args, **kwargs):
        if not getattr(env, 'name', None):
            abort(u'Remote server is not specified')
        func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def active_env(name, environ_name):
    """
    Подготовка окружения
    """
    env_params = getattr(local_env, name, None)
    if not env_params:
        abort(u"Не найдено окружение")

    # Имя пользователя от которого запущен проект
    env.user = env_params.get('user')

    # Хосты на которых расположен проект.
    env.hosts = env_params.get('host')

    for host in env.hosts:
        if host.find('@') != -1:
            abort(u"Хост и пароль должны указываться в разных настройках: `host` and `user`")

    # Папка в котором располагается проект
    env.root = env_params.get('root_dir')

    # Ветка по умолчанию для
    env.branch = env_params.get('branch')

    # Путь до virtualenv директории на серверах
    env.activate = env_params.get('venv')

    # Путь до virtualenv директории на серверах
    env.virtualenv = os.path.basename(os.path.dirname(os.path.dirname(env.activate)))

    # Путь до virtualenv директории на серверах
    env.supervisor = env_params.get('supervisor', None)
    env.is_supervisor_sudo = env_params.get('is-supervisor-sudo', False)

    env.is_bower_install  = env_params.get('is-bower-install', True)

    env.is_mysql = env_params.get('is-mysql', False)

    # Имя окружения
    env.name = environ_name


@task
def staging():
    """
    Подготовка окружения тестового сервера
    """
    active_env('STAGING_ENVIRONMENT', 'staging')


@task
def production():
    """
    Подготовка окружения рабочего сервера
    """
    active_env('PRODUCTION_ENVIRONMENT', 'production')


@task
@is_active_env
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
            local("git push origin %s" % branch)

    # Обновления в clever-tools
    if local_env.CLEVER_REVISION:
        virtualenv = os.environ.get('VIRTUAL_ENV', None)
        if local_env.CLEVER_REVISION != 'master':
            tools_branch = 'version/' + local_env.CLEVER_REVISION
        else:
            tools_branch = 'master'
        with lcd(os.path.join(virtualenv, 'src/clever-tools')):
            local('git push origin ' + tools_branch)

    with cd(env.root):
        # Обновляем бранчи если надо
        if branch != env.branch:
            run('git fetch --all')

        if force:
            run('git fetch --all')
            run('git reset --hard HEAD')

        # Перемещаем изменения из репозитория в локальную папку
        run('git pull origin ' + branch)
        run('git checkout ' + branch)

        # Обновляем исходный код для статических файлов
        if local_env.MARKUP_DIRECTORY:
            with cd(local_env.MARKUP_DIRECTORY):
                if force:
                    run('git fetch --all')
                    run('git reset --hard origin/master')
                else:
                    run('git pull origin %s' % branch)


@task
@is_active_env
def install(branch=None):
    """
    Установка зависимостей

    Аргументы:
        - :branch: Ветка из которой берутся изменения, по умолчанию текущий для окружения
    """
    with cd(env.root):
        # Обновляем зависимости для проекта
        with prefix(env.activate):
            if local_env.CLEVER_REVISION:
                if local_env.CLEVER_REVISION != 'master':
                    tools_branch = 'version/' + local_env.CLEVER_REVISION
                else:
                    tools_branch = 'master'
                run('pip install --upgrade -e git+git@bitbucket.org:cleversite/clever-tools.git@' + tools_branch + '#egg=clever-tools')
            run('pip install -r ' + local_env.REQUIREMENTS_NAME)


@task
@is_active_env
def backup():
    """Резервное копирование базы данных"""

    if env.is_mysql:
        dump_file = backup_mysql(local_env.BACKUP_DIRECTORY)
    else:
        dump_file = backup_postgre(local_env.BACKUP_DIRECTORY)

    context = {
        'dump': dump_file,
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
@is_active_env
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
    with cd(env.root):
        revert_mysql(data['dump'])


@task
@is_active_env
def copy_backup():
    """
    Копирование послежнего бэкапа на компьютер пользоватеоя
    """
    # Загружаем информацию о точке востоновления
    input = os.path.join(local_env.BACKUP_DIRECTORY, 'backup.json')
    output = os.path.join(local_env.BACKUP_DIRECTORY, '%(host)s-%(path)s')
    with cd(env.root):
        fullname = operations.get(input, local_path=output)[0]

        with open(fullname) as json_data:
            data = json.load(json_data)

        get(data['dump'], os.path.join(local_env.BACKUP_DIRECTORY, env.name + '.sql'))


@task
@is_active_env
def copy_media():
    media_root = get_django_setting('MEDIA_ROOT')

    with cd(os.path.dirname(media_root)):
        archive = os.path.join(env.root, local_env.BACKUP_DIRECTORY, 'media.tar.gz')
        run('tar -czvf %s %s --exclude=%s' % (archive, os.path.basename(media_root), os.path.join(os.path.basename(media_root), 'thumbs')))
        get(archive, os.path.join(local_env.BACKUP_DIRECTORY, env.name + '.tar.gz'))
        run('rm %s' % (archive))


@task
@is_active_env
def migrate(*args):
    """
    Миграция изменений схемы в БД
    """
    with cd(env.root):
        with prefix(env.activate):
            # Обновления БД в соответствии с джанго
            run('python manage.py syncdb')

            # Мигрируем изменения в БД
            run('python manage.py migrate ' + ' '.join(args))


@task
@is_active_env
def collect():
    """
    Сборка и обновление статических файлов проекта
    """
    # Собираем статические файлы
    with cd(env.root):
        with prefix(env.activate):
            if env.is_bower_install:
                run('npm install')
                run('$(npm bin)/bower install')
            run('python manage.py collectstatic --noinput')
            run('python manage.py generate_compress')


@task
@is_active_env
def restart():
    """
    Перезапуск приложения
    """
    with cd(env.root):
        with prefix(env.activate):
            if env.supervisor:
                if env.is_supervisor_sudo:
                    run('sudo supervisorctl restart %s:*' % env.supervisor)
                else:
                    run('supervisorctl restart %s:*' % env.supervisor)
            else:
                # Перезапуск приложения Django
                run('killall -u ' + env.user + ' ' + local_env.DJANGO_WSGI_NAME)


@task
@is_active_env
def flush_cache():
    """
    Сбросить кэш Reddis'а
    """
    run("echo 'FLUSHALL' | redis-cli")


@task
@is_active_env
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


@task
@is_active_env
def import_xml(*args):
    """
    Обновление каталога на сайте
    """
    # Собираем статические файлы
    with cd(env.root):
        with prefix(env.activate):
            with prefix('export PYTHONIOENCODING=utf-8'):
                run('python manage.py import_xml ' + ' '.join(args))


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
