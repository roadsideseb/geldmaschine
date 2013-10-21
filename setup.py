#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


setup(
    name='geldmaschine',
    version='0.0.1',
    description='A script to collect balance information from various online banking websites.',
    long_description=readme + '\n\n' + history,
    author='Sebastian Vetter',
    author_email='sebastian@roadside-developer.com',
    url='https://github.com/elbaschid/geldmaschine',
    packages=[
        'geldmaschine',
    ],
    package_dir={'geldmaschine': 'geldmaschine'},
    include_package_data=True,
    install_requires=[
        'splinter',
        'selenium',
        'requests',
        'docopt',
        'psutil',
        'beautifulsoup4',
        'blessings',
        'babel',
        'six',
        'keyring',
        'pycrypto',  # for encrypted file backend in keyring
        'jsonpickle',
    ],
    license="BSD",
    zip_safe=False,
    keywords='geldmaschine',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        #"Programming Language :: Python :: 2",
        #'Programming Language :: Python :: 2.6',
        #'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': ['geldmaschine = geldmaschine.main:main',]
    },
)
