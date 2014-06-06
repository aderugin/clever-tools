# -*- coding: utf-8 -*-
import sys
from clever.progress import AnimatedProgressBar


class ProcessLogger(object):
    """ Данный класс отвечает за вывод инофрмации о процессе """
    is_complete = False
    progress = None

    def initialize(self, count):
        self.progress = AnimatedProgressBar(width=80, end=count)

    def __add__(self, increment):
        if self.progress:
            self.progress += increment
            self.show_progress()
        return self

    def complete(self, message, *args, **kwargs):
        raise NotImplementedError()

    def notice(self, message, *args, **kwargs):
        raise NotImplementedError()

    def info(self, message, *args, **kwargs):
        raise NotImplementedError()

    def error(self, message, *args, **kwargs):
        raise NotImplementedError()

    def line(self, width=80):
        self.info(u'-' * width)

    def show_errors(self, errors):
        raise NotImplementedError()

    def show_progress(self):
        pass


class ConsoleProcessLogger(ProcessLogger):
    """ Данный класс отвечает за вывод инофрмации о процессе в термнал """
    def __init__(self, is_color=True, is_progress=True):
        self.is_color = is_color
        self.is_progress = is_progress

    def _write(self, message, *args, **kwargs):
        # TODO: Fix color as named argument!!!
        # format message
        string = message % (args)

        # create color string
        color = kwargs.pop('color', 'white')
        if color == 'red':
            string = '\033[31m' + string + '\033[39m'
        elif color == 'green':
            string = '\033[32m' + string + '\033[39m'
        elif color == 'blue':
            string = '\033[34m' + string + '\033[39m'

        # cleanup string
        if self.progress:
            sys.stdout.write('\r' + ' ' * (self.progress.width + 10) + '\r')
            sys.stdout.flush()

        # output message to console
        sys.stdout.write(string)
        if kwargs.pop('new_line', True):
            sys.stdout.write("\n")
        sys.stdout.flush()

        # show progress back to screen
        if not self.is_complete and self.progress:
            self.show_progress()

    def complete(self, message, *args, **kwargs):
        self.is_complete = True
        self._write(message, color='green', *args, **kwargs)

    def notice(self, message, *args, **kwargs):
        self._write(message, color='white', *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self._write(message, color='blue', *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._write(message, color='red', *args, **kwargs)

    def show_errors(self, errors):
        former_errors = set()

        if len(errors):
            for error in errors:
                exception_message = '%s' % error['exception']
                if not exception_message in former_errors:
                    self._write(exception_message, color='red')
                    former_errors.add(exception_message)

    def show_progress(self):
        if self.progress:
            self.progress.show_progress()


class CeleryProcessLogger(ProcessLogger):
    """ Данный класс отвечает за вывод информации о процессе в Celery """
    def __init__(self, task):
        self.task = task

    def complete(self, message, *args, **kwargs):
        pass

    def notice(self, message, *args, **kwargs):
        pass

    def info(self, message, *args, **kwargs):
        pass

    def error(self, message, *args, **kwargs):
        pass

    def show_errors(self, errors):
        pass

    def show_progress(self):
        from celery import current_task
        current_task.update_state(state='PROGRESS', meta={'description': 'Doing some task', 'current': 59, 'tota': 73})

        self.task.update_state(
            state='PROGRESS',
            meta={
                'progress': self.progress.progress
            }
        )