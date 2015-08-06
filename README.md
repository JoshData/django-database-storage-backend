# django-database-storage

A Django 1.7/1.8 storages backend backed by your existing database.

This module provides an app named `dbstorage`. The app contains a single model `StoredFile` which is where files stored with the storage backend are put. The app also provides `DatabaseStorage` which you can set on your file fields.

To use:

Put the `dbstorage` directory in your PYTHONPATH. (I'll make this installable at another time.)

Put `'dbstorage'` in your `INSTALLED_APPS` in your `settings.py`.

Add `DEFAULT_FILE_STORAGE = 'dbstorage.storage.DatabaseStorage'` to your `settings.py`.


Add to your `urls.py` URLconf:

	url(r'^user-media', include('dbstorage.urls')),

`user-media` determines the URL path where media files are accessed from. You can set this to anything.

Add a File or ImageFile field to your model:

	image = models.ImageField(upload_to='some-root')

`some-root` gets prefixed to all of the names of the files uploaded by this field. The names are stored in a database column.
