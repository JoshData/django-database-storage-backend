from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.core.files.base import ContentFile
from django.conf import settings

from .models import StoredFile, get_url_for_path

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
		try:
			sf = StoredFile.objects.get(path=name)
		except StoredFile.DoesNotExist:
			sf = StoredFile()

		sf.path = name
		sf.set_blob(content.read())
		sf.save()

		return name

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

