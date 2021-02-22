#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='django-database-storage-backend',
      version='1.0.0',
      description='A Django 1.10+/2.x storages backend backed by your existing database.',
      long_description=open("README.md", encoding='utf-8').read(),
      long_description_content_type='text/markdown',
      url='https://github.com/JoshData/django-database-storage-backend',
      keywords="Django storage database backend",

      classifiers=[ # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ],

      author='Joshua Tauberer',
      author_email='jt@occams.info',
      license='CC0',

      install_requires=["filemagic"],
      packages=['dbstorage'],
      provides=['dbstorage'],
      package_data={'dbstorage': ['migrations/*']},
)