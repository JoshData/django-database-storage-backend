from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_control

import os.path

from .models import StoredFile

@cache_control(public=True, max_age=60*60)
def get_file_content_view(request, path):

	try:
		sf = StoredFile.objects.get(path=path)
	except StoredFile.DoesNotExist:
		raise Http404()

	file_content = sf.get_blob()
	mime_type = sf.mime_type or "application/octet-stream"

	if "size" in request.GET:
		try:
			file_content = transform_image(file_content, request.GET['size'])
		except Exception as e:
			return HttpResponse(str(e), status=500)

	response = HttpResponse(file_content, content_type=mime_type)
	response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
	return response

def transform_image(file_content, size):
	import io
	from PIL import Image

	try:
		# Get the desired width from a small range of options.
		# 'tb' (thumbnail) is intended to be at least as good for og:image URLs,
		# which for twitter summary cards must be at least 120px.
		width = { 'tb': 320, 'xs': 768, 'sm': 1024, 'md': 1100, 'lg': 1400 }[size]
	except KeyError:
		return file_content

	# Resize the image and output at low quality jpeg to
	# reduce bandwidth usage.
	im = Image.open(io.BytesIO(file_content))
	im.thumbnail((width, width), Image.ANTIALIAS)
	buf = io.BytesIO()
	im.save(buf, "JPEG", quality=25, optimize=True, progressive=True)
	return buf.getvalue()
