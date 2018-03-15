from django.db import models
from django.urls import reverse
import urllib.parse

import base64
import magic
import zlib

# path.max_length is at least as large as the sum of:
# * the maximum length of any FileField's 'upload_to' attribute
# * the length of a SHA-1 hash in hex (40 characters)
# * a period and ten-character file extension (11 characters)
# and should not be larger than 255 because that is the
# maximum length for a MySQL char column with a UNIQUE
# index.
PATH_MAX_LENGTH = 255

class StoredFile(models.Model):
	"""A file stored in the storage."""

	path = models.CharField(db_index=True, unique=True, max_length=PATH_MAX_LENGTH, help_text="The file name of the stored file.")
	mime_type = models.CharField(max_length=128, blank=True, null=True, help_text="The MIME type of the stored file, if known.")

	value = models.TextField(help_text="The encoded binary data in this file.")

	size = models.IntegerField(db_index=True, help_text="The size of the stored file in bytes (the size of the actual file, not as it is stored).")
	encoded_size = models.IntegerField(db_index=True, help_text="The size of the stored file in bytes, as stored.")
	encoding = models.IntegerField(choices=[(0, "None."), (1, "Base 64")])
	gzipped = models.BooleanField()

	trusted = models.BooleanField(default=False, help_text="Is this file trusted to be served from our own domain?")

	created = models.DateTimeField(auto_now_add=True, db_index=True)
	updated = models.DateTimeField(auto_now=True, db_index=True)

	def __str__(self):
		return self.path

	def get_absolute_url(self):
		return get_url_for_path(self.path)

	def save(self, *args, **kwargs):
		super(StoredFile, self).save()

	def set_blob(self, data, compression=9):
		with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
			self.mime_type = m.id_buffer(data)
		if not self.mime_type:
			self.mime_type = "application/octet-stream"

		self.size = len(data)

		self.gzipped = True
		data = zlib.compress(data, compression)

		self.encoding = 1
		data = base64.b64encode(data).decode("ascii")

		self.value = data
		self.encoded_size = len(data)

	def get_blob(self):
		data = self.value

		if self.encoding == 1:
			data = base64.b64decode(data.encode("ascii"))
		else:
			raise ValueError()

		if self.gzipped:
			data = zlib.decompress(data)

		return data

def get_url_for_path(path):
	from .views import get_file_content_view # here because of circular dependency
	return reverse(get_file_content_view, args=[urllib.parse.quote_plus(path, safe='/')])
