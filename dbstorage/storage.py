from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.core.files.base import ContentFile
from django.conf import settings

from .models import StoredFile, get_url_for_path, PATH_MAX_LENGTH

import hashlib, mimetypes

@deconstructible
class DatabaseStorage(Storage):
	def __init__(self, options=None):
		self.options = options or getattr(settings, 'DATABASE_STORAGE', None)

	# REQUIRED METHODS

	def _open(self, name, mode='rb'):
		if mode != 'rb':
			raise ValueError("Only mode 'rb' is supported.")

		# Get the StoredFile. Raises a DoesNotExist exception if no file exists at that path.
		sf = StoredFile.objects.get(path=name)
		return ContentFile(sf.get_blob())

	def _save(self, name, content):
		# Read in the content.
		content = content.read()

		try:
			# Update an existing file if the name corresponds to an existing file.
			sf = StoredFile.objects.get(path=name)

		except StoredFile.DoesNotExist:
			# This name is for a new file. For privacy/security, don't use the file
			# name given to us. Instead, hash the content.
			name = DatabaseStorage.generate_name(name, content)
			try:
				# Still the file may exist. If it exists, the content is surely
				# the same. But we'll update anyway.
				sf = StoredFile.objects.get(path=name)
			except StoredFile.DoesNotExist:
				# Definitely a new file.
				sf = StoredFile()

		sf.path = name
		sf.set_blob(content)
		sf.save()

		return name

	@staticmethod
	def generate_name(name, content):
		# Preserve the path where the image is stored (this usually comes from
		# upload_to) but ignore the part after the last slash (the filename).
		new_name = ""
		if "/" in name:
			new_name = name.rsplit("/", 1)[0] + "/"

		# Replace the name with just the hash of the content.
		new_name += hashlib.sha256(content).hexdigest().lower()

		# If the name has a file extension, normalize the extension based
		# on the presumed MIME type of the extension.
		if "." in name:
			ext = name.rsplit(".", 1)[-1]
			mime_type, encoding = mimetypes.guess_type(name, strict=False)
			if mime_type:
				ext = mimetypes.guess_extension(mime_type, strict=False)
				if ext:
					new_name += ext

		return new_name[0:PATH_MAX_LENGTH]


	# TYPICALLY IMPLEMENTED

	def delete(self, name):
		StoredFile.objects.filter(path=name).delete()

	def exists(self, name):
		return StoredFile.objects.filter(path=name).exists()

	def listdir(self, path):
		if path.endswith('/'): path += '/'
		dirs = set()
		files = set()
		for sf in StoredFile.objects.filter(path__startswith=path):
			fn = sf.path[len(path):].split('/', 1)
			if len(fn) == 1:
				# Just one component in the path -- it's a file right here.
				files.add(fn[0])
			elif len(fn) > 1:
				# There are path components, so add the top directory name.
				dirs.add(fn[0])
		return (sorted(dirs), sorted(files))

	def size(self, name):
		return StoredFile.objects.get(path=name).size

	def url(self, name):
		return get_url_for_path(name)

	# ADDITIONAL METHODS

	# accessed_time - not implemented

	def created_time(self, name):
		# should return a naive datetime!
		return StoredFile.objects.get(path=name).created

	def modified_time(self, name):
		# should return a naive datetime!
		return StoredFile.objects.get(path=name).updated

