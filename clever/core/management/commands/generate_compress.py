# -*- coding: utf-8 -*-
import subprocess
from subprocess import PIPE
from clever.path import ensure_dir
from django.core.cache import get_cache
from django.core.management.base import BaseCommand
from django.conf import settings
from optparse import make_option
import os


COMPRESS_SCRIPT_BIN = '$(npm bin)/r.js -o {infile} out={outfile}'
COMPRESS_STYLE_BIN = '$(npm bin)/lessc {infile} {outfile} --clean-css -rp {static_url}'


class SubprocessError(Exception):
    pass


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        # make_option('--cleanup', action='store_true', help='Remove old classes'),
    )

    def run_process(self, command_line, directory):
        process = subprocess.Popen(command_line, stdout=PIPE, stderr=PIPE, shell=True, cwd=directory)
        result = process.wait()
        if result > 0:
            error_string = process.stderr.read()
            output_string = process.stdout.read()
            import ipdb; ipdb.set_trace()
            raise SubprocessError(error_string if error_string else output_string)

    def compile_script(self, input_file, output_file):
        print "Compile script:", output_file

        input_file = os.path.join(settings.STATIC_PATH, input_file)
        output_file = os.path.join(settings.STATIC_PATH, output_file)

        directory = os.path.dirname(output_file)
        ensure_dir(directory)

        self.run_process(COMPRESS_SCRIPT_BIN.format(infile=input_file, outfile=output_file), directory=directory)

    def compile_styles(self, input_file, output_file):
        print "Compile style:", output_file

        input_file = os.path.join(settings.STATIC_PATH, input_file)
        output_file = os.path.join(settings.STATIC_PATH, output_file)

        directory = os.path.dirname(output_file)
        ensure_dir(directory)

        command = COMPRESS_STYLE_BIN.format(infile=input_file, outfile=output_file, static_url=settings.STATIC_URL)

        self.run_process(command, directory=directory)

    def handle(self, source_file=None, *args, **kwargs):
        # get compress version and increment it
        cache = get_cache('default')
        version = cache.get('CLEVER_COMPRESS_VERSION', 0)
        version += 1

        # compress styles and script
        self.compile_styles('less/styles.less', 'compress/style.%d.css' % version)
        self.compile_script('js/build.js', 'compress/script.%d.js' % version)

        # store new version
        cache.set('CLEVER_COMPRESS_VERSION', version)