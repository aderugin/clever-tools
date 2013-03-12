import os
from setuptools import setup, find_packages
import clever


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="clever",
    version=clever.__version__,
    long_description=read('README.md'),
    keywords='',
    packages=find_packages(),
    author='Clever Promo',
    author_email='it@clever-site.ru',
    url="",
    include_package_data=True,
    test_suite='clever.tests.runtests.runtests',
    install_requires=[
        # Concrete version
        'Django == 1.5',
        'django-cache-machine == 0.6',

        # Latest version
        'FeinCMS >= 1.7.1',
        'PIL >= 1.1.7',
        'South >= 0.7.6',
        'Unidecode >= 0.04.12',
        'django-autoslug >= 1.6.1',
        'django-ckeditor >= 3.6.2.1',
        'django-cleanup >= 0.1.6',
        'django-compressor >= 1.2',
        'django-extensions >= 1.1.0',
        'django-importer >= 0.5',
        'django-model-utils >= 1.2.0',
        'django-mptt >= 0.5',
        'docutils >= 0.10',
        'ordereddict >= 1.1',
        'pytils >= 0.2.3',
        'sorl-thumbnail >= 11.12',

        #'git+git://github.com/alurin/django-whatever.git',
        #'git+git://github.com/django-mptt/django-mptt.git',
    ]
)
