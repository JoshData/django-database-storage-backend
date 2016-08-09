#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='django-database-storage',
      version='0.0.1',
      description='A Django 1.7/1.8/1.9 storages backend backed by your existing database.',
      author='Joshua Tauberer',
      author_email='jt@occams.info',
      install_requires=[],
      packages=['dbstorage'],
      provides=['dbstorage'],
      package_data={'dbstorage': ['migrations/*']},
)