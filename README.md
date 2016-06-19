# django-database-storage

A Django 1.7/1.8/1.9 storages backend backed by your existing database.

This module provides an app named `dbstorage`. The app contains a single model `StoredFile` which is where files stored with the storage backend are put. The app also provides `DatabaseStorage` which you can set on your file fields.

## Usage

Put the `dbstorage` directory in your PYTHONPATH. (I'll make this installable at another time.)

Put `'dbstorage'` in your `INSTALLED_APPS` in your `settings.py`.

Add `DEFAULT_FILE_STORAGE = 'dbstorage.storage.DatabaseStorage'` to your `settings.py`.

Add to your `urls.py` URLconf:

	url(r'^user-media', include('dbstorage.urls')),

`user-media` determines the URL path where media files are accessed from. You can set this to anything.

Add a File or ImageFile field to your model:

	image = models.ImageField(upload_to='some-root')

`some-root/` gets prefixed to all of the names of the files uploaded by this field. The names are stored in a database column.

## Features

* Easily configure a media storage backend that just uses your existing database for storing and serving your media files.
* Filenames are replaced with the SHA256 hash of the file content, so you don't have to worry about leaking the name of the file when it was originally uploaded.
* MIME type autodetection (based on the file extension).
* The backend supports `delete`, `exists`, `listdir`, `size`, `url`, `created_time`, and `modified_time`.
* Stored files appear in the Django admin.

## Dynamic image resizing

When storing images, the view method can automatically resize an image to one of a few pre-defined sizes. To use this feature, you must install `pillow`. Then add `?width=` plus `xs` (768px), `sm` (1024 px), `md` (1100px), or `lg` (1400px) to the URL when accessing the image. The image returned in the response will have this size as a maximum dimension.
