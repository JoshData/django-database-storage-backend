# django-database-storage

A Django 1.10-2.0 storages backend backed by your existing database.

This module provides an app named `dbstorage`. The app contains a single model `StoredFile` which is where files stored with the storage backend are put. The app also provides `DatabaseStorage` which you can set on your file fields.

## Usage

Install libmagic, e.g.:

	brew install libmagic

Install this package:

	pip django-database-storage-backend

Put `'dbstorage'` in your `INSTALLED_APPS` in your `settings.py`.

Add to your `settings.py`:

	DEFAULT_FILE_STORAGE = 'dbstorage.storage.DatabaseStorage'

Add to your `urls.py` URLconf:

	url(r'^user-media/', include('dbstorage.urls')),

`user-media/` determines the URL path where media files are accessed from. You can set this to anything.

Add a File or ImageFile field to your model:

	image = models.ImageField(upload_to='some-root')

Files saved into this field will be stored in the database and available at the URL path `/user-media/some-root/{HASH}.{EXT}`. `HASH` is the SHA-1 hash of the file content. The file extension is replaced with a normalized file extension by auto-detecting the file type so that no file name information besides the file's type is leaked. This also prevents unauthorized users from randomly guessing the URLs to uploaded files.

## Features

* Easily configure a media storage backend that just uses your existing database for storing and serving your media files.
* Filenames don't leak the name of the file that it was uploaded from and are based on a hash of the file's content to prevent unauthorized users from guessing file URLs.
* Secure headers are set to prevent untrusted content from being a cross-site scripting vulnerability.
* The backend supports the `delete`, `exists`, `listdir`, `size`, `url`, `created_time`, and `modified_time` functions.
* Stored files appear in the Django admin.

## Dynamic image resizing

When storing images, the view method can automatically resize an image to one of a few pre-defined sizes. To use this feature, you must install `pillow`. Then add `?width=` plus `xs` (768px), `sm` (1024 px), `md` (1100px), or `lg` (1400px) to the URL when accessing the image. The image returned in the response will have this size as a maximum dimension.

For Project Maintainers
-----------------------

To publish a universal wheel to pypi::

        pip3 install twine
        rm -rf dist
        python3 setup.py bdist_wheel --universal
        twine upload dist/*
        git tag v1.0.XXX
        git push --tags
