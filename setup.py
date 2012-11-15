import sys

# Prevent spurious errors during `python setup.py test`, a la
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html:
try:
    import multiprocessing
except ImportError:
    pass

from setuptools import setup, find_packages


extra_setup = {}
if sys.version_info >= (3,):
    extra_setup['use_2to3'] = True

setup(
***REMOVED***
    version='1.0',
    description='Various utilities for operating on dates and times',
    long_description=open('README.rst').read(),
    author='Erik Rose',
***REMOVED***
    packages=find_packages(exclude=['ez_setup']),
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',
***REMOVED***
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        ],
    keywords=['date', 'parse', 'time'],
    **extra_setup
)
