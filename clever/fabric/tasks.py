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
from clever.fabric.utils import backup_mysql
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

    'init',
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

    env.is_bower_install  = env_params.get('is-bower-install', True)

    env.is_supervisor_with_sudo = env_params.get('supervisor-with-sudo', False)

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


@task
@is_active_env
def restart():
    """
    Перезапуск приложения
    """
    with cd(env.root):
        with prefix(env.activate):
            if env.supervisor:
                if env.is_supervisor_with_sudo:
                    run('sudo supervisorctl restart %s' % ' '.join(env.supervisor))
                else:
                    run('supervisorctl restart %s' % ' '.join(env.supervisor))
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


@task
@is_active_env
def init():
    ''' Провести подготовку сервера и развернуть приложения '''

    class Step:
        prompt = None
        func = None
        variables = None

        def __init__(self, prompt, func):
            self.prompt = prompt
            self.func = func

        def init_variables(self, builder):
            if not self.variables:
                import inspect
                self.variables = []
                res = inspect.getargspec(self.func)
                for arg in res.args:
                    if arg in builder.variables:
                        self.variables.append(arg)
            return self.variables

        def __call__(self, builder):
            kwargs = {}
            for name in self.variables:
                kwargs[name] = builder.variables[name].get(builder)
            return self.func(builder, **kwargs)

    class Variable(object):
        name = None
        value = None
        is_loaded = False
        default = ''
        func = None
        prompt = None
        section = None
        is_secure = False

        def __init__(self, name, prompt, section, func, is_secure=False, default='', required=False):
            self.name = name
            self.prompt = prompt
            self.section = section
            self.func = func
            self.default = default
            self.required = required
            self.is_secure = is_secure

        def raw_input(self):
            message = self.prompt + ":"
            if self.section:
                message = '[' + self.section + '] ' + message
            message = green(message)
            return operations.prompt(message, default=self.default)

        def read(self, builder):
            value = self.raw_input()
            self.set(self.func(builder, value))

        def get(self, builder):
            if not self.is_loaded:
                self.read(builder)
            return self.value

        def set(self, value):
            self.is_loaded = True
            self.value = value

    class Flag(Variable):
        def raw_input(self):
            message = self.prompt + " [y/n]?"
            if self.section:
                message = '[' + self.section + '] ' + message
            message = green(message)
            default = 'y' if self.default else 'n'
            return 'y' == operations.prompt(message, default=default, validate='^[yn]$')


    class Builder:
        steps    = None
        variables = None

        def __init__(self):
            self.steps = []
            self.variables = {}
            self.variables_list = []

        def step(self, prompt):
            def wrapper(func):
                step = Step(prompt, func)
                self.steps.append(step)
                return func
            return wrapper

        def variable(self, prompt, section=None, secure=False, default='', required=False):
            def wrapper(func):
                var = Variable(func.__name__, prompt, section, func, is_secure=secure, default=default, required=required)
                self.register_var(var)
                return func
            return wrapper

        def flag(self, prompt, section=None, secure=False, default=False, required=False):
            def wrapper(func):
                var = Flag(func.__name__, prompt, section, func, is_secure=secure, default=default, required=required)
                self.register_var(var)
                return func
            return wrapper

        def register_var(self, var):
            self.variables[var.name] = var
            self.variables_list.append(var)

        def load_variables(self):
            import ConfigParser as configparser
            config = configparser.SafeConfigParser()
            config.read('deploy-%s.conf' % env.name)

            for section in config.sections():
                for name, value in config.items(section):
                    if name in self.variables:
                        var = self.variables[name]
                        if not var.is_secure:
                            var.set(value)

        def save_variables(self):
            import ConfigParser as configparser
            config = configparser.SafeConfigParser()

            for var in self.variables_list:
                if not var.is_secure and var.is_loaded:
                    if not config.has_section(var.section):
                        config.add_section(var.section)
                    config.set(var.section, var.name, unicode(var.get(self)))
            with open('deploy-%s.conf' % env.name, "w+") as f:
                config.write(f)

        def run(self):
            idx       = 1
            count     = len(self.steps)
            steps     = []
            variables = []

            # Collect steps
            for step in self.steps:
                is_active = operations.prompt("Step %d/%d: %s [y/n]?" % (idx, count, step.prompt), default='n', validate='^[yn]$')
                if is_active == 'y':
                    steps.append(step)
                    variables += step.init_variables(self)
                idx += 1

            # Load variables
            self.load_variables()
            for var in self.variables_list:
                if var.name in variables:
                    var.get(self)
            self.save_variables()

            # Start steps
            idx   = 1
            count = len(steps)
            for step in steps:
                print "## ============= %d/%d %s" % (idx, count, blue(step.prompt))
                step(self)
                idx += 1

    builder = Builder()
    project_name, settings_name = local_env.DJANGO_SETTINGS.rsplit(".", 1)

    ##--------------------------------------------------------------------------
    # Настройки пакетов
    @builder.variable("Название репозитория с проектом", section="Repository", default=(u'%s-django' % project_name))
    def django_repository(builder, value):
        return 'git@bitbucket.org:cleversite/%s.git' % value

    ##--------------------------------------------------------------------------
    # Настройки для репозиотриев
    @builder.variable("Название репозитория с проектом", section="Repository", default=(u'%s-django' % project_name))
    def django_repository(builder, value):
        return 'git@bitbucket.org:cleversite/%s.git' % value

    @builder.variable("Название репозитория с версткой", section="Repository", default=(u'%s-markup' % project_name))
    def markup_repository(builder, value):
        return 'git@bitbucket.org:cleversite/%s.git' % value

    ##--------------------------------------------------------------------------
    # Настройки для баззы данных
    @builder.variable("Пользователь базы данных", section="MySQL", default='root')
    def mysql_user(builder, value):
        return value

    @builder.variable("Пароль базы данных", section="MySQL", secure=True)
    def mysql_password(builder, value):
        return value

    @builder.variable("Имя базы данных", section="MySQL", default=project_name)
    def mysql_database(builder, value):
        return value

    ##--------------------------------------------------------------------------
    # Настройки веб сервера
    @builder.variable("Относительный путь к публичной папке веб сервера", section='VHost', default='www')
    def vhost_path(builder, value):
        return value

    @builder.variable("Имя сайта", section='VHost', default=('%s.ru' % project_name))
    def vhost_name(builder, value):
        return value

    @builder.variable("Порт для Gunicorn", section='VHost', default=9090)
    def vhost_port(builder, value):
        return value

    ##--------------------------------------------------------------------------
    # Настройки проекта
    @builder.variable("DSN для Sentry", section='Raven', default=9090)
    def raven_dsn(builder, value):
        return value

    ##--------------------------------------------------------------------------
    # Настройки сервера
    @builder.flag("Установить библиотеку клиента для MariaDB", section="Feature", default=True)
    def is_mariadb(builder, value):
        return value

    @builder.flag("Установить поисковой движок Xapian", section="Feature", default=False)
    def is_xapian(builder, value):
        return value

    @builder.flag("Установить подержку Celery", section="Feature", default=False)
    def is_celery(builder, value):
        return value

    ##--------------------------------------------------------------------------
    @builder.step(prompt='Установка недостоющих пакетов в системе')
    def configure_packages(builder, is_xapian, is_mariadb, is_celery):
        packages = [
            "git",
            "build-essential",
            "libssl-dev",
            "zlib1g-dev",
            "python-dev",
            "libjpeg8-dev",
            "libpng12-dev",
            "supervisor",
            "redis-server",
        ]

        # Зависимости для Xapian
        if is_xapian:
            packages += ['uuid-dev']

        # Зависимости для MySQL
        if is_mariadb:
            packages += ["libmariadbclient-dev"]
        else:
            packages += ["libmysqlclient-dev"]

        # Зависимости для Celery
        if is_celery:
            packages += ["rabbitmq-server"]

        # Устанавливаем нужные пакеты для проекта
        with settings(user='root'):
            install_packages(*packages)

    ##--------------------------------------------------------------------------
    @builder.step(prompt='Первоначальная настройка Apache')
    def configure_apache_conf(builder):
        with settings(user='root'):
            template = os.path.join(os.path.dirname(__file__), '.fabric/apache/mod_clever.conf')
            files.upload_template(template, '/etc/apache2/mods-enabled/mod_clever.conf')

            run('a2enmod proxy')
            with settings(warn_only=True):
                run('service apache2 restart')

    ##--------------------------------------------------------------------------
    @builder.step(prompt='Первоначальная настройка Supervisor')
    def configure_supervisor_conf(builder):
        with settings(user='root'):
            template = os.path.join(os.path.dirname(__file__), '.fabric/supervisor/mod_clever.conf')
            files.upload_template(template, '/etc/supervisor/conf.d/mod_clever.conf')

            run('supervisorctl reload')

    ##--------------------------------------------------------------------------
    @builder.step(prompt='Слить репозитории проекта')
    def configure_repository(self, django_repository, markup_repository):
        run('mkdir -p %s' % env.root)
        with cd(env.root):
            # Создаем новый экземпляр

            # Вытаскиваем репозиторий проекта
            run('git init')
            run('git remote add origin %s' % django_repository)
            run('git fetch --all')
            run('git checkout -b master origin/master')

            if local_env.MARKUP_DIRECTORY:
                run('git clone %s %s' % (markup_repository, local_env.MARKUP_DIRECTORY))

    ##--------------------------------------------------------------------------
    @builder.step(prompt='Создание локальных настроек для проекта')
    def configure_local_settings(self, mysql_database, mysql_user, mysql_password, vhost_name, vhost_path, raven_dsn):
        context = {
            'project_name': project_name,
            'dbname':       mysql_database,
            'dbuser':       mysql_user,
            'dbpass':       mysql_password,
            'hostname':     vhost_name,
            'secret_key':   generate_secret_key(),
            'static_path':  os.path.join(env.root, vhost_path, 'static'),
            'media_path':   os.path.join(env.root, vhost_path, 'media'),
            'dsn':          raven_dsn,
        }
        template = os.path.join(os.path.dirname(__file__), '.fabric', 'local_settings.py.dist')
        output = os.path.join(env.root, project_name, 'local_settings.py')
        files.upload_template(template, output, context=context)

    ##--------------------------------------------------------------------------
    @builder.step(prompt='Создание скрипты для Supervisor\'а')
    def configure_supervisor_scripts(self, vhost_name, vhost_port):
        context = {
            'project_name': project_name,
            'project_path': env.root,
            'python_path': os.path.join(env.root, env.virtualenv, 'bin/python'),
            'settings_module': local_env.DJANGO_SETTINGS,
            'hostname': vhost_name,
            'username': env.user,
            'port': vhost_port,
        }

        with settings(user='root'):
            # Настраиваем Gunicorn
            template = os.path.join(os.path.dirname(__file__), '.fabric/supervisor/web.conf')
            files.upload_template(template, '/etc/supervisor/conf.d/%s-web.conf' % project_name, context)

            if is_celery:
                # Настраиваем Celery Worker
                template = os.path.join(os.path.dirname(__file__), '.fabric/supervisor/worker.conf')
                files.upload_template(template, '/etc/supervisor/conf.d/%s-worker.conf' % project_name, context)

                # Настраиваем Celery Stats
                template = os.path.join(os.path.dirname(__file__), '.fabric/supervisor/stats.conf')
                files.upload_template(template, '/etc/supervisor/conf.d/%s-stats.conf' % project_name, context)

    ##--------------------------------------------------------------------------
    # Создаем базу в MySQl
    @builder.step(prompt='Создание базы данных MySQL')
    def configure_database(self, mysql_user, mysql_password, mysql_database):
        with cd(env.root):
            with hide('running'):
                run('mysql -u%s -p%s -e "CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;"' % (mysql_user, mysql_password, mysql_database))

    ##--------------------------------------------------------------------------
    # Создаем виртуальное окружение для Python
    @builder.step(prompt='Создание виртуального окружения')
    def configure_virtualenv(self):
        with cd(env.root):
            run('virtualenv %s' % env.virtualenv)

            with prefix(env.activate):
                if not is_python27():
                    with hide('output'):
                        run('pip install --upgrade -e git+git@bitbucket.org:cleversite/clever-tools.git@version/' + local_env.CLEVER_REVISION + '#egg=clever-tools')
                    run('clever-install-python')
                    run('rm -rf %s/lib/python2.6/' % env.virtualenv)

    ##--------------------------------------------------------------------------
    @builder.step(prompt='Создание настроек Apache (.htaccess)')
    def configure_htaccess(self, vhost_port):
        template = os.path.join(os.path.dirname(__file__), '.fabric/apache/.htaccess')
        files.upload_template(template, os.path.join(env.root, vhost_path, '.htaccess'), {
            'port': vhost_port,
        })

    ##--------------------------------------------------------------------------
    # Обычное развертывание сайта
    @builder.step(prompt='Развернуть проект')
    def deploy_project(self, is_xapian):
        if is_xapian:
            with cd(env.root):
                with prefix(env.activate):
                    run('clever-install-xapian')
        install()
        migrate()
        collect()
        restart()

    # Запускаем инсталяцию
    builder.run()


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
