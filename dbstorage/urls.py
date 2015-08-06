from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^/(.*)', 'dbstorage.views.get_file_content_view', name='get_file_content_view'),
)
