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


def get_mysql_params():
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

    params = get_mysql_params()
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


def revert_mysql(fullname):
    params = get_mysql_params()
    with cd(env.root):
        run('mysql -u%s -p%s %s < %s' % (
            params['db_user'],
            params['db_pass'],
            params['db_name'],
            fullname
            ))
