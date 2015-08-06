from django.db import models
from django.core.urlresolvers import reverse
import urllib.parse

import base64
import mimetypes
import zlib

class StoredFile(models.Model):
	"""A file stored in the storage."""

		# max_length is at least as large as the default for
		# the FileField plus the maximum length of any upload_to.
	path = models.CharField(db_index=True, unique=True, max_length=256, help_text="The file name of the stored file.")
	mime_type = models.CharField(max_length=128, blank=True, null=True, help_text="The MIME type of the stored file, if known.")

	value = models.TextField(help_text="The encoded binary data in this file.")

	size = models.IntegerField(db_index=True, help_text="The size of the stored file in bytes (the size of the actual file, not as it is stored).")
	encoded_size = models.IntegerField(db_index=True, help_text="The size of the stored file in bytes, as stored.")
	encoding = models.IntegerField(choices=[(0, "None."), (1, "Base 64")])
	gzipped = models.BooleanField()

	created = models.DateTimeField(auto_now_add=True, db_index=True)
	updated = models.DateTimeField(auto_now=True, db_index=True)

	def __str__(self):
		return self.path

	def get_absolute_url(self):
		return get_url_for_path(self.path)

	def save(self, *args, **kwargs):
		# Guess MIME type if not set explicitly.
		if self.mime_type == None:
			mime_type, encoding = mimetypes.guess_type(self.path)
			self.mime_type = mime_type

		super(StoredFile, self).save()


	def set_blob(self, data, compression=9):
		self.size = len(data)

		self.gzipped = True
		data = zlib.compress(data, compression)

		self.encoding = 1
		data = base64.b64encode(data)

		self.value = data
		self.encoded_size = len(data)

		self.mime_type = None

	def get_blob(self):
		data = self.value

		if self.encoding == 1:
			data = base64.b64decode(data)

		if self.gzipped:
			data = zlib.decompress(data)

		return data

def get_url_for_path(path):
	from .views import get_file_content_view # here because of circular dependency
	return reverse(get_file_content_view, args=[urllib.parse.quote_plus(path, safe='/')])