# -*- coding: utf-8 -*-
import django_nose

class PatchedNoseTestSuiteRunner(django_nose.NoseTestSuiteRunner):
    """
    Поправки для запуска тестов для Django:
        - Создание таблиц для моделей расположенных в tests.py
    """
    def run_tests(self, test_labels, extra_tests=None):
        self.build_suite(test_labels, extra_tests)
        return super(PatchedNoseTestSuiteRunner, self).run_tests(
            test_labels=test_labels, extra_tests=extra_tests)
