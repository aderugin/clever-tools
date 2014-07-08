# -*- coding: utf-8 -*-
from fabric.api import run
from fabric.api import env
from fabric.api import cd
from fabric.api import prefix
from fabric.api import hide
from clever.fabric import local_env
import os


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


console_line = "DJANGO_SETTINGS_MODULE=%s python -c \"from django.conf import settings; print settings.%s\""
def get_django_setting(name):
    with cd(env.root):
        with prefix(env.activate):
            with hide('output', 'running'):
                return run(console_line % (local_env.DJANGO_SETTINGS, name))


def get_default_database_params():
    console_line = "DJANGO_SETTINGS_MODULE=%s python -c \"from django.conf import settings; print settings.DATABASES['default']['%s']\""
    with cd(env.root):
        with prefix(env.activate):
            with hide('output', 'running'):
                params = {
                    'db_user': run(console_line % (local_env.DJANGO_SETTINGS, "USER")),
                    'db_pass': run(console_line % (local_env.DJANGO_SETTINGS, "PASSWORD")),
                    'db_name': run(console_line % (local_env.DJANGO_SETTINGS, "NAME")),
                }
    return params


def backup_mysql(path):
    from datetime import datetime
    dump_file = str(datetime.now()).replace(':', '_').replace(' ', '_') + '.sql'
    fullname = os.path.join(path, dump_file)

    params = get_default_database_params()
    with cd(env.root):
        run('mkdir -p %s' % path)

        with hide('running'):
            run('mysqldump -u%s -p%s %s > %s' % (
                params['db_user'],
                params['db_pass'],
                params['db_name'],
                fullname
                ))
    return fullname


def backup_postgre(path):
    from datetime import datetime
    dump_file = str(datetime.now()).replace(':', '_').replace(' ', '_') + '.sql'
    fullname = os.path.join(path, dump_file)

    params = get_default_database_params()
    with cd(env.root):
        run('mkdir -p %s' % path)

        with hide('running'):
            run('PGPASSWORD=%s pg_dump -U %s %s > %s' % (
                params['db_pass'],
                params['db_name'],
                params['db_user'],
                fullname
            ))
    return fullname

def revert_mysql(fullname):
    params = get_default_database_params()
    with cd(env.root):
        run('mysql -u%s -p%s %s < %s' % (
            params['db_user'],
            params['db_pass'],
            params['db_name'],
            fullname
            ))


def install_packages(*packages):
    ''' Проверить существование пакетов на сервере '''
    with hide('output'):
        run('apt-get update')

    run('apt-get install -q -y %s' % ' '.join(packages))


def is_python27():
    with hide('output', 'running'):
        result = run('python --version')
        return result.startswith("Python 2.7")


def generate_secret_key():
    with hide('output', 'running'):
        result = run("python -c \"import random; print (''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789\!@#$%^&*(-_=+)') for i in range(50)]))\"")
        return result.encode('utf-8')
