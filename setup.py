#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='django-database-storage-backend',
      version='0.0.3',
      description='A Django 1.10+ storages backend backed by your existing database.',
      author='Joshua Tauberer',
      author_email='jt@occams.info',
      install_requires=["filemagic"],
      packages=['dbstorage'],
      provides=['dbstorage'],
      package_data={'dbstorage': ['migrations/*']},
)