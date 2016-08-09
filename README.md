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

Files saved into this field will be stored in the database and available at the URL path `/user-media/some-root/{SHA1HASH}.{EXT}`. SHA1HASH is the SHA-1 hash of the file content. The file extension is normalized from the uploaded file's file extension (by round-tripping through [mimetypes.guess_type](https://docs.python.org/3.5/library/mimetypes.html#mimetypes.guess_type) and [mimetypes.guess_extension](https://docs.python.org/3.5/library/mimetypes.html#mimetypes.guess_extension)), so that no file name information besides the file's type is leaked. This also prevents unauthorized users from randomly guessing the URLs to uploaded files.

## Features

* Easily configure a media storage backend that just uses your existing database for storing and serving your media files.
* Filenames don't leak the name of the file that it was uploaded from and are based on the file hash to prevent unauthorized users from guessing file URLs.
* MIME type autodetection for the Content-Type header when downloading files (based on the file extension).
* The backend supports the `delete`, `exists`, `listdir`, `size`, `url`, `created_time`, and `modified_time` functions.
* Stored files appear in the Django admin.

## Dynamic image resizing

When storing images, the view method can automatically resize an image to one of a few pre-defined sizes. To use this feature, you must install `pillow`. Then add `?width=` plus `xs` (768px), `sm` (1024 px), `md` (1100px), or `lg` (1400px) to the URL when accessing the image. The image returned in the response will have this size as a maximum dimension.
