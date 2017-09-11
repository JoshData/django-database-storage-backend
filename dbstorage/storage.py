from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.core.files.base import ContentFile
from django.conf import settings

from .models import StoredFile, get_url_for_path, PATH_MAX_LENGTH

import hashlib, mimetypes, os.path
import magic

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

	def _save(self, name, content_file):
		# Read in the content.
		content_file.open()
		try:
			content = content_file.read()
		finally:
			content_file.close()

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
		# Replace the name with just the hash of the content. Since we have limited
		# space to store the name, use SHA1 rather than SHA256.
		new_name = hashlib.sha1(content).hexdigest().lower()

		# Generate a file extension to make downloads have nice file names.
		# Determine the MIME type from the content.
		with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
			mime_type = m.id_buffer(content)

		# Then choose a canonical extension. Cap at 10 characters.
		ext = mimetypes.guess_extension(mime_type, strict=False)
		if ext:
			new_name += ext[:10]

		# Preserve the path where the image is stored (this usually comes from
		# upload_to) -- ignore the part after the last slash (the filename).
		# Also make sure this doesn't bump the hash out of the max length.
		if os.path.dirname(name):
			new_name = os.path.dirname(name)[:PATH_MAX_LENGTH-len(new_name)-1] + "/" + new_name

		# Return the name. For sanity's sake, ensure it's not longer than what
		# we can store.
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
		return StoredFile.objects.only("size").get(path=name).size

	def url(self, name):
		return get_url_for_path(name)

	# ADDITIONAL METHODS

	# accessed_time - not implemented

	def created_time(self, name):
		# should return a naive datetime!
		return StoredFile.objects.only("created").get(path=name).created

	def modified_time(self, name):
		# should return a naive datetime!
		return StoredFile.objects.only("updated").get(path=name).updated

