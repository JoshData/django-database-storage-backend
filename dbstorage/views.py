from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_control

import os.path

from .models import StoredFile

@cache_control(public=True, max_age=60*60*3)
def get_file_content_view(request, path):
	# Get the StoredFile instance or 404 if the path is not found.
	try:
		sf = StoredFile.objects.get(path=path)
	except StoredFile.DoesNotExist:
		raise Http404()

	# Get the file content.
	file_content = sf.get_blob()

	# Choose the MIME type and disposition. For security, to prevent
	# user-uploaded executable content from being served on our domain,
	# which would be a cross-site scripting vulnerability, use headers
	# that prevent content from being executed.
	mime_type = "application/octet-stream"
	disposition = "attachment"

	# Allow trusted files to be viewed on our domain without downloading.
	# Browsers won't execute "image/*" content, so those are safe to provide
	# as images.
	if sf.trusted or (sf.mime_type and sf.mime_type.startswith("image/")):
		# If the file knows its MIME type, use it.
		if sf.mime_type:
			mime_type = sf.mime_type

		# Allow it to be viewed in the browser.
		disposition = "inline"

	# Post-process images.
	if "size" in request.GET or "blur" in request.GET or "quality" in request.GET or "brightness" in request.GET:
		try:
			file_content, mime_type = transform_image(file_content, request.GET)
		except Exception as e:
			return HttpResponse(str(e), status=500)

	# Form the HTTP response.
	response = HttpResponse(file_content, content_type=mime_type)
	response['Content-Disposition'] = disposition + '; filename=' + os.path.basename(path)

	# Browsers may guess the MIME type if it thinks it is wrong. Prevent
	# that so that if we are forcing application/octet-stream, it
	# doesn't guess around it and make the content executable.
	response['X-Content-Type-Options'] = 'nosniff'

	# Browsers may still allow HTML to be rendered in the browser. IE8
	# apparently rendered HTML in the context of the domain even when a
	# user clicks "Open" in an attachment-disposition response. This
	# prevents that. Doesn't seem to affect anything else (like images).
	response['X-Download-Options'] = 'noopen'

	return response

def transform_image(file_content, options):
	import io
	from PIL import Image, ImageFilter, ImageEnhance

	# Load the image.
	im = Image.open(io.BytesIO(file_content))

	# Blur, if specified.
	if options.get('blur'):
		im = im.filter(ImageFilter.GaussianBlur(radius=3))

	# Change lightness, if specified.
	if options.get('brightness'):
		im = ImageEnhance.Brightness(im).enhance(float(options['brightness']))

	# Resize, if specified.

	# Get the desired width from a small range of options.
	# 'tb' (thumbnail) is intended to be at least as good for og:image URLs,
	# which for twitter summary cards must be at least 120px.
	width = { 'tb': 320, 'xs': 768, 'sm': 1024, 'md': 1100, 'lg': 1400 }.get(options.get('size'))

	# Resize the image and output at low quality jpeg to
	# reduce bandwidth usage.
	if width:
		im.thumbnail((width, width), Image.ANTIALIAS)

	# Re-serialize to JPEG.
	buf = io.BytesIO()
	if options.get('quality') == 'low':
		im.save(buf, "JPEG", quality=33, optimize=True, progressive=True)
	else:
		im.save(buf, "JPEG")
	return (buf.getvalue(), "image/jpeg")
