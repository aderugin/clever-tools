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
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    keywords='',
    packages=find_packages(),
    author='Clever Promo',
    author_email='it@clever-site.ru',
    url="",
    include_package_data=True,
    test_suite='clever.tests.runtests.runtests',
)
