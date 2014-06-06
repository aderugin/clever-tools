# -*- coding: utf-8 -*-
import sys

class Progress:
    """ Класс отвечает за информирование о прогрессе заданий """
    def print_errors(self, errors=None):
        pass

    def error(self, message, **args, **kwargs):
        pass

    def info(self, message, **args, **kwargs):
        pass


class ConsoleProgress(Progress):
    def text_color(*args, **kwargs):
        color = kwargs.get('color', 'green')
        string = u''.join(args)
        if color == 'red':
            return '\033[31m' + string + '\033[39m'
        return '\033[32m' + string + '\033[39m'

    def info(self, message, **args, **kwargs):
        color = kwargs.get('color', 'green')


    def error(self, message, **args, **kwargs):
        color = kwargs.get('color', 'red')

    def flush(self):
        sys.stdout.flush()

    def print_errors(self, errors=None):
        former_errors = set()
        if errors is None:
            errors = self.errors

        if len(errors):
            for error in errors:
                exception_message = '%s' % error['exception']
                if not exception_message in former_errors:
                    sys.stdout.write(''.join(["    - Информация об ошибке: \n\033[31m", exception_message, "\033[39m\n"]))
                    former_errors.add(exception_message)


class CeleryProgress(Progress):
    pass