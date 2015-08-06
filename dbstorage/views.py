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

	response = HttpResponse(file_content, content_type=mime_type)
	response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
	return response